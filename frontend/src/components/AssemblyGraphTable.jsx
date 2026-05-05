import React, { useMemo, useState, useEffect, useRef } from "react";

export default function AssemblyGraphTable({ assemblyGraph, fitmentProfiles, fitmentResults, loading, error }) {
  const [viewMode, setViewMode] = useState("table"); // "table" or "graph"
  const canvasRef = useRef(null);
  
  // Build assembly graph from fitment results instead of LLM graph
  // This ensures we show ALL validated mechanical connections
  const computedAssemblyGraph = useMemo(() => {
    if (!fitmentResults || fitmentResults.length === 0) {
      return assemblyGraph || {}; // Fallback to LLM graph if no fitment results
    }
    
    const graph = {};
    
    // Only include THREAD connections (actual mating relationships)
    fitmentResults.forEach(result => {
      if (result.interface_type === 'THREAD') {
        const partA = result.part_a;
        const partB = result.part_b;
        
        // Add bidirectional edges
        if (!graph[partA]) graph[partA] = [];
        if (!graph[partB]) graph[partB] = [];
        
        if (!graph[partA].includes(partB)) {
          graph[partA].push(partB);
        }
        if (!graph[partB].includes(partA)) {
          graph[partB].push(partA);
        }
      }
    });
    
    return graph;
  }, [fitmentResults, assemblyGraph]);
  
  // Convert graph to edge list for display
  const edges = useMemo(() => {
    if (!computedAssemblyGraph || typeof computedAssemblyGraph !== 'object') return [];
    
    const edgeSet = new Set();
    const edgeList = [];
    
    for (const [partA, mates] of Object.entries(computedAssemblyGraph)) {
      if (!Array.isArray(mates)) continue;
      
      for (const partB of mates) {
        // Create a canonical edge key (alphabetically sorted) to avoid duplicates
        const edgeKey = [partA, partB].sort().join('|');
        
        if (!edgeSet.has(edgeKey)) {
          edgeSet.add(edgeKey);
          edgeList.push({ partA, partB });
        }
      }
    }
    
    return edgeList;
  }, [computedAssemblyGraph]);

  // Extract unique nodes from edges
  const nodes = useMemo(() => {
    const nodeSet = new Set();
    edges.forEach(({ partA, partB }) => {
      nodeSet.add(partA);
      nodeSet.add(partB);
    });
    return Array.from(nodeSet);
  }, [edges]);

  // Graph visualization using canvas
  useEffect(() => {
    if (viewMode !== "graph" || !canvasRef.current || nodes.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    
    // Set canvas size with device pixel ratio for crisp rendering
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Physics simulation for node positions
    const nodePositions = new Map();
    const nodeRadius = 30;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;

    // Position nodes in a circle
    nodes.forEach((node, i) => {
      const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2;
      nodePositions.set(node, {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      });
    });

    // Get theme colors from CSS variables
    const computedStyle = getComputedStyle(document.documentElement);
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const edgeColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';
    const nodeColor = isDark ? '#3b82f6' : '#2563eb';
    const textColor = isDark ? '#e5e7eb' : '#1f2937';
    const nodeBorder = isDark ? '#60a5fa' : '#1d4ed8';

    // Helper function to draw arrow
    const drawArrow = (fromX, fromY, toX, toY, color) => {
      const headLength = 12;
      const angle = Math.atan2(toY - fromY, toX - fromX);
      
      // Draw line
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(fromX, fromY);
      ctx.lineTo(toX, toY);
      ctx.stroke();
      
      // Draw arrowhead
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(toX, toY);
      ctx.lineTo(
        toX - headLength * Math.cos(angle - Math.PI / 6),
        toY - headLength * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        toX - headLength * Math.cos(angle + Math.PI / 6),
        toY - headLength * Math.sin(angle + Math.PI / 6)
      );
      ctx.closePath();
      ctx.fill();
    };

    // Draw edges with arrows and labels
    const edgeLabelColor = isDark ? '#9ca3af' : '#6b7280';
    edges.forEach(({ partA, partB }, index) => {
      const posA = nodePositions.get(partA);
      const posB = nodePositions.get(partB);
      if (posA && posB) {
        // Calculate direction vector
        const dx = posB.x - posA.x;
        const dy = posB.y - posA.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const unitX = dx / distance;
        const unitY = dy / distance;
        
        // Adjust start and end points to account for node radius
        const startX = posA.x + unitX * nodeRadius;
        const startY = posA.y + unitY * nodeRadius;
        const endX = posB.x - unitX * nodeRadius;
        const endY = posB.y - unitY * nodeRadius;
        
        // Draw arrow
        drawArrow(startX, startY, endX, endY, edgeColor);
        
        // Draw edge label at midpoint
        const midX = (posA.x + posB.x) / 2;
        const midY = (posA.y + posB.y) / 2;
        
        // Get connection details from fitmentProfiles
        let labelText = 'mates';
        if (fitmentProfiles && fitmentProfiles[partA] && fitmentProfiles[partB]) {
          const profileA = fitmentProfiles[partA];
          const profileB = fitmentProfiles[partB];
          
          // Determine if A is male (screw) or female (hole)
          const isAMale = profileA.gender === 'male';
          const isBFemale = profileB.gender === 'female';
          
          if (isAMale && isBFemale) {
            // A is male (screw), B is female (holes)
            // For screws, use the thread count (usually just one thread spec per screw)
            let threadCount = 0;
            if (profileA.threads && profileA.threads.length > 0) {
              // Use the first thread's count (this is the screw count from BOM)
              threadCount = profileA.threads[0].count;
            }
            
            // For holes, try to find a matching hole pattern count
            // Look for hole patterns that match the thread count
            let holeCount = 0;
            if (profileB.hole_patterns && profileB.hole_patterns.length > 0) {
              // Try to find a hole pattern with matching count
              const matchingHole = profileB.hole_patterns.find(h => h.count === threadCount);
              if (matchingHole) {
                holeCount = matchingHole.count;
              } else {
                // If no exact match, use the first hole pattern
                holeCount = profileB.hole_patterns[0].count;
              }
            }
            
            if (threadCount && holeCount) {
              labelText = `${threadCount} → ${holeCount}`;
            } else if (threadCount) {
              labelText = `${threadCount} screws`;
            } else if (holeCount) {
              labelText = `${holeCount} holes`;
            }
          } else if (!isAMale && profileB.gender === 'male') {
            // B is male (screw), A is female (holes) - reverse case
            let threadCount = 0;
            if (profileB.threads && profileB.threads.length > 0) {
              threadCount = profileB.threads[0].count;
            }
            
            let holeCount = 0;
            if (profileA.hole_patterns && profileA.hole_patterns.length > 0) {
              const matchingHole = profileA.hole_patterns.find(h => h.count === threadCount);
              if (matchingHole) {
                holeCount = matchingHole.count;
              } else {
                holeCount = profileA.hole_patterns[0].count;
              }
            } else if (profileA.threads && profileA.threads.length > 0) {
              // Female part might have threads (tapped holes)
              holeCount = profileA.threads[0].count;
            }
            
            if (threadCount && holeCount) {
              labelText = `${holeCount} ← ${threadCount}`;
            } else if (threadCount) {
              labelText = `${threadCount}`;
            } else if (holeCount) {
              labelText = `${holeCount}`;
            }
          } else {
            // Both same gender or other case - try to show any available counts
            const countA = (profileA.threads && profileA.threads.length > 0) 
              ? profileA.threads[0].count 
              : (profileA.hole_patterns && profileA.hole_patterns.length > 0)
                ? profileA.hole_patterns[0].count
                : 0;
            const countB = (profileB.threads && profileB.threads.length > 0)
              ? profileB.threads[0].count
              : (profileB.hole_patterns && profileB.hole_patterns.length > 0)
                ? profileB.hole_patterns[0].count
                : 0;
            
            if (countA && countB) {
              labelText = `${countA} ↔ ${countB}`;
            } else if (countA) {
              labelText = `${countA}`;
            } else if (countB) {
              labelText = `${countB}`;
            }
          }
        }
        
        // Draw label background
        ctx.font = '10px sans-serif';
        const labelMetrics = ctx.measureText(labelText);
        const labelPadding = 4;
        const labelWidth = labelMetrics.width + labelPadding * 2;
        const labelHeight = 16;
        
        ctx.fillStyle = isDark ? 'rgba(31, 41, 55, 0.9)' : 'rgba(255, 255, 255, 0.9)';
        ctx.fillRect(
          midX - labelWidth / 2,
          midY - labelHeight / 2,
          labelWidth,
          labelHeight
        );
        
        // Draw label text
        ctx.fillStyle = edgeLabelColor;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(labelText, midX, midY);
      }
    });

    // Draw nodes
    nodes.forEach((node) => {
      const pos = nodePositions.get(node);
      if (!pos) return;

      // Draw node circle
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, nodeRadius, 0, 2 * Math.PI);
      ctx.fillStyle = nodeColor;
      ctx.fill();
      ctx.strokeStyle = nodeBorder;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw node label
      ctx.fillStyle = textColor;
      ctx.font = '11px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Wrap text if too long
      const maxWidth = nodeRadius * 1.8;
      const text = node;
      const metrics = ctx.measureText(text);
      
      if (metrics.width > maxWidth) {
        // Split into two lines
        const mid = Math.floor(text.length / 2);
        const line1 = text.substring(0, mid);
        const line2 = text.substring(mid);
        ctx.fillText(line1, pos.x, pos.y - 6);
        ctx.fillText(line2, pos.x, pos.y + 6);
      } else {
        ctx.fillText(text, pos.x, pos.y);
      }
    });

  }, [viewMode, nodes, edges, fitmentProfiles]);

  if (loading) {
    return (
      <div style={{ 
        flex: 1, 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        color: "var(--color-text-secondary)",
        fontSize: "var(--text-sm)"
      }}>
        Processing assembly relationships...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        flex: 1, 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        flexDirection: "column",
        gap: 8,
        color: "var(--color-text-secondary)",
        fontSize: "var(--text-sm)"
      }}>
        <div style={{ color: "var(--color-error)", fontWeight: 500 }}>Error loading assembly graph</div>
        <div>{error}</div>
      </div>
    );
  }

  if (!computedAssemblyGraph || Object.keys(computedAssemblyGraph).length === 0) {
    return (
      <div style={{ 
        flex: 1, 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        flexDirection: "column",
        gap: 12,
        color: "var(--color-text-secondary)",
        fontSize: "var(--text-sm)",
        padding: 24
      }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.3">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v4M12 16h.01"/>
        </svg>
        <div style={{ fontWeight: 500 }}>No assembly graph available</div>
        <div style={{ textAlign: "center", maxWidth: 400 }}>
          Upload a drawing to see which parts physically mate with each other.
        </div>
      </div>
    );
  }

  if (edges.length === 0) {
    return (
      <div style={{ 
        flex: 1, 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        flexDirection: "column",
        gap: 12,
        color: "var(--color-text-secondary)",
        fontSize: "var(--text-sm)",
        padding: 24
      }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.3">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <div style={{ fontWeight: 500 }}>No mating relationships found</div>
        <div style={{ textAlign: "center", maxWidth: 400 }}>
          The assembly graph is empty. This may indicate that no parts were identified as mating.
        </div>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
      {/* Summary header with view toggle */}
      <div style={{ 
        padding: "12px 16px", 
        borderBottom: "1px solid var(--color-border)",
        background: "var(--color-surface)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
        fontSize: "var(--text-sm)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="5" r="3"/>
              <circle cx="12" cy="19" r="3"/>
              <circle cx="5" cy="12" r="3"/>
              <circle cx="19" cy="12" r="3"/>
              <line x1="12" y1="8" x2="12" y2="16"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
            <span style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>
              {edges.length} Mating Relationship{edges.length !== 1 ? 's' : ''}
            </span>
          </div>
          <div style={{ color: "var(--color-text-tertiary)" }}>•</div>
          <div style={{ color: "var(--color-text-secondary)" }}>
            {Object.keys(computedAssemblyGraph).length} Part{Object.keys(computedAssemblyGraph).length !== 1 ? 's' : ''} in Assembly
          </div>
        </div>

        {/* View mode toggle */}
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: 4,
          background: "var(--color-bg)",
          borderRadius: 6,
          padding: 2
        }}>
          <button
            onClick={() => setViewMode("table")}
            style={{
              padding: "6px 12px",
              fontSize: "var(--text-xs)",
              fontWeight: 500,
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
              background: viewMode === "table" ? "var(--color-surface)" : "transparent",
              color: viewMode === "table" ? "var(--color-text-primary)" : "var(--color-text-secondary)",
              transition: "all 0.15s ease",
              display: "flex",
              alignItems: "center",
              gap: 6,
              boxShadow: viewMode === "table" ? "0 1px 2px rgba(0,0,0,0.05)" : "none"
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
            </svg>
            Table
          </button>
          <button
            onClick={() => setViewMode("graph")}
            style={{
              padding: "6px 12px",
              fontSize: "var(--text-xs)",
              fontWeight: 500,
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
              background: viewMode === "graph" ? "var(--color-surface)" : "transparent",
              color: viewMode === "graph" ? "var(--color-text-primary)" : "var(--color-text-secondary)",
              transition: "all 0.15s ease",
              display: "flex",
              alignItems: "center",
              gap: 6,
              boxShadow: viewMode === "graph" ? "0 1px 2px rgba(0,0,0,0.05)" : "none"
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="5" r="2"/>
              <circle cx="5" cy="12" r="2"/>
              <circle cx="19" cy="12" r="2"/>
              <circle cx="12" cy="19" r="2"/>
              <line x1="12" y1="7" x2="12" y2="17"/>
              <line x1="7" y1="12" x2="17" y2="12"/>
            </svg>
            Graph
          </button>
        </div>
      </div>

      {/* Content area */}
      {viewMode === "table" ? (
        <div style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--text-sm)" }}>
          <thead style={{ 
            position: "sticky", 
            top: 0, 
            background: "var(--color-surface)", 
            zIndex: 1,
            borderBottom: "2px solid var(--color-border)"
          }}>
            <tr>
              <th style={{ 
                padding: "10px 16px", 
                textAlign: "left", 
                fontWeight: 600,
                color: "var(--color-text-secondary)",
                fontSize: "var(--text-xs)",
                textTransform: "uppercase",
                letterSpacing: "0.05em"
              }}>
                #
              </th>
              <th style={{ 
                padding: "10px 16px", 
                textAlign: "left", 
                fontWeight: 600,
                color: "var(--color-text-secondary)",
                fontSize: "var(--text-xs)",
                textTransform: "uppercase",
                letterSpacing: "0.05em"
              }}>
                Part A
              </th>
              <th style={{ 
                padding: "10px 16px", 
                textAlign: "center", 
                fontWeight: 600,
                color: "var(--color-text-secondary)",
                fontSize: "var(--text-xs)",
                width: 60
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: "block", margin: "0 auto" }}>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </th>
              <th style={{ 
                padding: "10px 16px", 
                textAlign: "left", 
                fontWeight: 600,
                color: "var(--color-text-secondary)",
                fontSize: "var(--text-xs)",
                textTransform: "uppercase",
                letterSpacing: "0.05em"
              }}>
                Part B
              </th>
            </tr>
          </thead>
          <tbody>
            {edges.map((edge, idx) => (
              <tr 
                key={`${edge.partA}-${edge.partB}`}
                style={{ 
                  borderBottom: "1px solid var(--color-border)",
                  transition: "background-color 0.15s ease"
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--color-hover)"}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
              >
                <td style={{ 
                  padding: "12px 16px",
                  color: "var(--color-text-tertiary)",
                  fontWeight: 500,
                  fontSize: "var(--text-xs)"
                }}>
                  {idx + 1}
                </td>
                <td style={{ 
                  padding: "12px 16px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "var(--text-sm)",
                  color: "var(--color-text-primary)",
                  fontWeight: 500
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{
                      width: 6,
                      height: 6,
                      borderRadius: "50%",
                      background: "var(--color-brand)",
                      flexShrink: 0
                    }} />
                    {edge.partA}
                  </div>
                </td>
                <td style={{ 
                  padding: "12px 16px",
                  textAlign: "center"
                }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-tertiary)" strokeWidth="2" style={{ display: "block", margin: "0 auto" }}>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <line x1="19" y1="12" x2="5" y2="12"/>
                    <polyline points="12 5 19 12 12 19"/>
                    <polyline points="12 19 5 12 12 5"/>
                  </svg>
                </td>
                <td style={{ 
                  padding: "12px 16px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "var(--text-sm)",
                  color: "var(--color-text-primary)",
                  fontWeight: 500
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{
                      width: 6,
                      height: 6,
                      borderRadius: "50%",
                      background: "var(--color-info)",
                      flexShrink: 0
                    }} />
                    {edge.partB}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      ) : (
        <div style={{ 
          flex: 1, 
          minHeight: 0, 
          display: "flex", 
          alignItems: "center", 
          justifyContent: "center",
          padding: 24,
          position: "relative"
        }}>
          <canvas
            ref={canvasRef}
            style={{
              width: "100%",
              height: "100%",
              maxWidth: 800,
              maxHeight: 600
            }}
          />
        </div>
      )}

      {/* Footer info */}
      <div style={{ 
        padding: "10px 16px", 
        borderTop: "1px solid var(--color-border)",
        background: "var(--color-surface)",
        fontSize: "var(--text-xs)",
        color: "var(--color-text-tertiary)",
        display: "flex",
        alignItems: "center",
        gap: 6
      }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        Assembly graph built from validated fitment connections. All mechanically compatible thread relationships are shown.
      </div>
    </div>
  );
}
