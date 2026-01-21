import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./ResultCard.css";

function ResultCard({ title, content }) {
  // Extract emoji and text from title
  const titleEmoji = title.match(/^[\p{Emoji}]/u)?.[0] || "";
  const titleText = title.replace(/^[\p{Emoji}]\s*/u, "");

  return (
    <div className="result-card">
      <div className="result-card-header">
        {titleEmoji && <span className="result-card-icon">{titleEmoji}</span>}
        <h3 className="result-card-title">{titleText}</h3>
      </div>
      <div className="result-card-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // Custom heading styles
            h1: ({ node, children, ...props }) => <h1 className="md-h1" {...props}>{children}</h1>,
            h2: ({ node, children, ...props }) => <h2 className="md-h2" {...props}>{children}</h2>,
            h3: ({ node, children, ...props }) => <h3 className="md-h3" {...props}>{children}</h3>,

            // Custom paragraph
            p: ({ node, ...props }) => <p className="md-p" {...props} />,

            // Custom lists
            ul: ({ node, ...props }) => <ul className="md-ul" {...props} />,
            ol: ({ node, ...props }) => <ol className="md-ol" {...props} />,
            li: ({ node, ...props }) => <li className="md-li" {...props} />,

            // Custom table
            table: ({ node, ...props }) => (
              <div className="md-table-wrapper">
                <table className="md-table" {...props} />
              </div>
            ),
            th: ({ node, ...props }) => <th className="md-th" {...props} />,
            td: ({ node, ...props }) => <td className="md-td" {...props} />,

            // Strong/Bold text
            strong: ({ node, ...props }) => <strong className="md-strong" {...props} />,

            // Code blocks
            code: ({ node, inline, ...props }) =>
              inline
                ? <code className="md-code-inline" {...props} />
                : <code className="md-code-block" {...props} />,

            // Blockquotes for important info
            blockquote: ({ node, ...props }) => <blockquote className="md-blockquote" {...props} />,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}

export default ResultCard;
