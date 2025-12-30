import ReactMarkdown from "react-markdown";

function ResultCard({ title, content }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}

export default ResultCard;
