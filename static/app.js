const $ = id => document.getElementById(id);

$("resume").addEventListener("change", () => {
  $("fileName").textContent = $("resume").files[0]?.name || "No file selected";
});

$("resumeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = $("resume").files[0];
  if (!file) return;

  $("status").textContent = "Analyzing resume...";
  const fd = new FormData();
  fd.append("file", file);

  try {
    const res = await fetch("/api/analyze", {method:"POST", body:fd});
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Analysis failed");
    render(data);
    loadHistory();
    $("status").textContent = "Analysis complete.";
  } catch(err) {
    $("status").textContent = "Error: " + err.message;
  }
});

function render(data) {
  $("results").classList.remove("hidden");
  const a = data.analysis;
  $("score").textContent = a.score + "/100";
  $("scoreText").textContent =
    a.score >= 80 ? "Excellent starting point." :
    a.score >= 60 ? "Good, but there is room for improvement." :
    "Needs improvement before applying.";

  $("skills").innerHTML = a.skills.length
    ? a.skills.map(s => `<span class="chip">${s}</span>`).join("")
    : "<span class='small'>No known skills detected.</span>";

  $("details").innerHTML = `
    <p><b>Words:</b> ${a.word_count}</p>
    <p><b>Sections:</b> ${Object.entries(a.sections).filter(x=>x[1]).map(x=>x[0]).join(", ") || "None detected"}</p>
  `;

  $("suggestions").innerHTML = a.suggestions.map(s => `<li>${s}</li>`).join("");

  $("jobs").innerHTML = data.recommendations.map(job => `
    <div class="job">
      <h3>${job.title}</h3>
      <div class="small">${job.company} • ${job.location}</div>
      <div class="match ${job.match >= 70 ? "good" : "warn"}">${job.match}% match</div>
      <p><b>Matched:</b> ${job.matched_skills.join(", ") || "None"}</p>
      <p><b>Skill gaps:</b> ${job.missing_skills.join(", ") || "None"}</p>
    </div>
  `).join("");
}

$("jobForm").addEventListener("submit", async e => {
  e.preventDefault();
  const payload = {
    title: $("jobTitle").value,
    company: $("company").value || "Custom Company",
    description: $("jobDescription").value,
    skills: $("jobSkills").value.split(",").map(x=>x.trim().toLowerCase()).filter(Boolean)
  };

  $("customResult").textContent = "Calculating...";
  const res = await fetch("/api/match-job", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    $("customResult").textContent = data.detail || "Error";
    return;
  }
  $("customResult").innerHTML = `
    <div class="job">
      <h3>${data.title}</h3>
      <div class="match ${data.match >= 70 ? "good" : "warn"}">${data.match}% match</div>
      <p><b>Matched skills:</b> ${data.matched_skills.join(", ") || "None"}</p>
      <p><b>Skill gaps:</b> ${data.missing_skills.join(", ") || "None"}</p>
    </div>`;
});

async function loadHistory() {
  const res = await fetch("/api/history");
  const rows = await res.json();
  if (!rows.length) return;
  $("history").innerHTML = rows.map(r =>
    `<div class="job"><b>${r.filename}</b> — Score ${r.score}/100 <span class="small">(${r.created_at})</span></div>`
  ).join("");
}
loadHistory();
