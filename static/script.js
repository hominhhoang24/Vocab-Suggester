document.addEventListener("DOMContentLoaded", function () {

  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", () => {
      const btn = form.querySelector("button[type='submit']");
      btn.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2"></span>
        Đang phân tích...
      `;
      btn.disabled = true;
      btn.style.opacity = "0.7";
    });
  }

  const sentenceEl = document.getElementById("sentence-text");
  if (!sentenceEl) return;

  // Từ ban đầu
  let currentWord = sentenceEl.dataset.focus;

  document.querySelectorAll(".replace-word").forEach((btn) => {
    btn.addEventListener("click", () => {
      const newWord = btn.dataset.word;

      const highlighted = sentenceEl.querySelector(".highlight-word");

      if (highlighted) {
        highlighted.outerHTML = `<span class="highlight-word">${newWord}</span>`;
        currentWord = newWord;
        return;
      }

      let html = sentenceEl.innerHTML;
      const regex = new RegExp(`\\b${currentWord}\\b`, "i");

      if (!regex.test(html)) {
        alert("Không tìm thấy từ để thay.");
        return;
      }

      sentenceEl.innerHTML = html.replace(
        regex,
        `<span class="highlight-word">${newWord}</span>`
      );

      currentWord = newWord;
    });
  });

});