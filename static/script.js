// =============================
// EduGenie Common JavaScript
// =============================

// Smooth scroll to top
window.addEventListener("load", () => {
    window.scrollTo(0, 0);
});

// Highlight active navigation link
document.addEventListener("DOMContentLoaded", () => {

    const current = window.location.pathname;

    document.querySelectorAll(".nav-links a").forEach(link => {

        if (link.getAttribute("href") === current) {
            link.classList.add("active");
        }

    });

});

// Future common functions can be added here.

// Markdown Parser Helper
function renderMarkdown(text) {
    if (!text) return "";

    if (typeof marked !== "undefined" && typeof marked.parse === "function") {
        return `<div class="markdown-body">${marked.parse(text)}</div>`;
    }

    let str = String(text);

    // Code blocks
    str = str.replace(/```([a-zA-Z]*)\n([\s\S]*?)```/g, function(match, lang, code) {
        return `<pre class="code-block"><code>${code.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre>`;
    });

    // Inline code
    str = str.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    // Headings
    str = str.replace(/^### (.*$)/gim, '<h3 class="md-heading">$1</h3>');
    str = str.replace(/^## (.*$)/gim, '<h2 class="md-heading">$1</h2>');
    str = str.replace(/^# (.*$)/gim, '<h1 class="md-heading">$1</h1>');

    // Horizontal Rule
    str = str.replace(/^---$/gim, '<hr class="md-hr">');

    // Bold & Italics
    str = str.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    str = str.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Bullet list items
    str = str.replace(/^[\*\-] (.*$)/gim, '<li class="md-item">$1</li>');

    let paragraphs = str.split(/\n\n+/);
    let result = paragraphs.map(p => {
        if (p.startsWith('<h') || p.startsWith('<pre') || p.startsWith('<hr')) {
            return p;
        }
        if (p.includes('<li class="md-item">')) {
            return `<ul class="md-list">${p}</ul>`;
        }
        return `<p class="md-p">${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    return `<div class="markdown-body">${result}</div>`;
}