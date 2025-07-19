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
