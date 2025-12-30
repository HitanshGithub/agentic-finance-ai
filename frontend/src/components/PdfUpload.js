import axios from "axios";

function PdfUpload({ setExpenses }) {
  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    const res = await axios.post(
      "http://127.0.0.1:8000/upload-pdf",
      form
    );

    const raw = res.data.expenses;

    // 🔥 NORMALIZE TO ARRAY
    let normalized = [];

    if (Array.isArray(raw)) {
      normalized = raw;
    } else if (typeof raw === "object") {
      normalized = Object.entries(raw).map(([category, amount]) => ({
        category,
        amount
      }));
    } else {
      alert("Could not parse expenses from PDF");
      return;
    }

    setExpenses(normalized);
  };

  return (
    <input type="file" accept=".pdf" onChange={upload} />
  );
}

export default PdfUpload;
