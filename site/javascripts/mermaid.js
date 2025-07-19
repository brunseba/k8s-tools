// Mermaid configuration for K8s Tools documentation

document.addEventListener('DOMContentLoaded', function() {
  // Initialize Mermaid with custom configuration
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    themeVariables: {
      primaryColor: '#326ce5',
      primaryTextColor: '#ffffff',
      primaryBorderColor: '#0f1419',
      lineColor: '#326ce5',
      secondaryColor: '#f8f9fa',
      tertiaryColor: '#dee2e6',
      background: '#ffffff',
      mainBkg: '#326ce5',
      secondBkg: '#f8f9fa',
      tertiaryBkg: '#e9ecef'
    },
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis'
    },
    sequence: {
      diagramMarginX: 50,
      diagramMarginY: 10,
      actorMargin: 50,
      width: 150,
      height: 65,
      boxMargin: 10,
      boxTextMargin: 5,
      noteMargin: 10,
      messageMargin: 35,
      mirrorActors: true,
      bottomMarginAdj: 1,
      useMaxWidth: true,
      rightAngles: false,
      showSequenceNumbers: false
    },
    gantt: {
      titleTopMargin: 25,
      barHeight: 20,
      fontFamily: '"Roboto", "Helvetica Neue", Arial, sans-serif',
      fontSize: 11,
      fontWeight: 400,
      gridLineStartPadding: 35,
      leftPadding: 75,
      topPadding: 50,
      bottomPadding: 50,
      rightPadding: 75
    }
  });

  // Add responsive behavior for mobile devices
  function updateMermaidForMobile() {
    const isMobile = window.innerWidth <= 768;
    const mermaidElements = document.querySelectorAll('.mermaid');
    
    mermaidElements.forEach(element => {
      if (isMobile) {
        element.style.transform = 'scale(0.8)';
        element.style.transformOrigin = 'top left';
      } else {
        element.style.transform = 'none';
        element.style.transformOrigin = 'initial';
      }
    });
  }

  // Update on window resize
  window.addEventListener('resize', updateMermaidForMobile);
  
  // Initial check
  updateMermaidForMobile();

  // Add click handlers for diagram interactions
  document.addEventListener('click', function(event) {
    if (event.target.closest('.mermaid')) {
      const diagram = event.target.closest('.mermaid');
      
      // Add a subtle highlight effect when clicked
      diagram.style.outline = '2px solid #326ce5';
      diagram.style.outlineOffset = '4px';
      
      // Remove highlight after 2 seconds
      setTimeout(() => {
        diagram.style.outline = 'none';
        diagram.style.outlineOffset = '0';
      }, 2000);
    }
  });

  // Handle diagram rendering errors gracefully
  window.addEventListener('error', function(event) {
    if (event.message && event.message.includes('mermaid')) {
      console.warn('Mermaid diagram rendering error:', event.message);
      
      // Find all mermaid elements and add error fallback
      const mermaidElements = document.querySelectorAll('.mermaid');
      mermaidElements.forEach(element => {
        if (element.innerHTML.trim() && !element.querySelector('svg')) {
          element.innerHTML = `
            <div style="
              border: 2px dashed #dc3545;
              padding: 1rem;
              text-align: center;
              color: #dc3545;
              background: #f8f9fa;
              border-radius: 4px;
            ">
              <strong>Diagram Rendering Error</strong><br>
              <small>Unable to render Mermaid diagram. Please check the syntax.</small>
            </div>
          `;
        }
      });
    }
  });

  // Add print-specific styles for diagrams
  const printStyles = document.createElement('style');
  printStyles.textContent = `
    @media print {
      .mermaid {
        break-inside: avoid;
        page-break-inside: avoid;
      }
      .mermaid svg {
        max-width: 100% !important;
        height: auto !important;
      }
    }
  `;
  document.head.appendChild(printStyles);

  // Enhance accessibility for screen readers
  document.querySelectorAll('.mermaid').forEach(diagram => {
    if (!diagram.getAttribute('role')) {
      diagram.setAttribute('role', 'img');
      diagram.setAttribute('aria-label', 'Architecture diagram showing system components and relationships');
    }
  });
});

// Export configuration for use in other scripts
window.k8sToolsMermaidConfig = {
  theme: 'default',
  primaryColor: '#326ce5',
  backgroundColor: '#ffffff'
};

// Mermaid initialization for MkDocs Material
document.addEventListener("DOMContentLoaded", function() {
    mermaid.initialize({
        startOnLoad: true,
        theme: "default",
        themeVariables: {
            primaryColor: "#1976d2",
            primaryTextColor: "#ffffff",
            primaryBorderColor: "#1565c0",
            lineColor: "#666666",
            sectionBkgColor: "#f5f5f5",
            altSectionBkgColor: "#ffffff",
            gridColor: "#e0e0e0",
            secondaryColor: "#bbdefb",
            tertiaryColor: "#e3f2fd"
        },
        flowchart: {
            htmlLabels: true,
            curve: "linear"
        },
        er: {
            entityPadding: 15,
            stroke: "#333333",
            fill: "#f9f9f9"
        },
        sequence: {
            diagramMarginX: 50,
            diagramMarginY: 10,
            actorMargin: 50,
            width: 150,
            height: 65,
            boxMargin: 10,
            boxTextMargin: 5,
            noteMargin: 10,
            messageMargin: 35,
            mirrorActors: true,
            bottomMarginAdj: 1,
            useMaxWidth: true,
            rightAngles: false,
            showSequenceNumbers: false
        },
        gantt: {
            titleTopMargin: 25,
            barHeight: 20,
            fontFamily: '"Open Sans", sans-serif',
            fontSize: 11,
            fontWeight: "normal",
            gridLineStartPadding: 35,
            bottomPadding: 5,
            numberSectionStyles: 4
        }
    });

    // Handle theme switching for Material theme
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === "attributes" && mutation.attributeName === "data-md-color-scheme") {
                const scheme = document.body.getAttribute("data-md-color-scheme");
                const theme = scheme === "slate" ? "dark" : "default";
                
                mermaid.initialize({
                    theme: theme,
                    themeVariables: scheme === "slate" ? {
                        primaryColor: "#90caf9",
                        primaryTextColor: "#000000",
                        primaryBorderColor: "#64b5f6",
                        lineColor: "#ffffff",
                        sectionBkgColor: "#424242",
                        altSectionBkgColor: "#616161",
                        gridColor: "#666666",
                        secondaryColor: "#1e88e5",
                        tertiaryColor: "#0d47a1"
                    } : {
                        primaryColor: "#1976d2",
                        primaryTextColor: "#ffffff",
                        primaryBorderColor: "#1565c0",
                        lineColor: "#666666",
                        sectionBkgColor: "#f5f5f5",
                        altSectionBkgColor: "#ffffff",
                        gridColor: "#e0e0e0",
                        secondaryColor: "#bbdefb",
                        tertiaryColor: "#e3f2fd"
                    }
                });
                
                // Re-render all mermaid diagrams
                const mermaidElements = document.querySelectorAll(".mermaid");
                mermaidElements.forEach(function(element) {
                    element.removeAttribute("data-processed");
                });
                mermaid.init();
            }
        });
    });

    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"]
    });
});
