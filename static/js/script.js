(function () {
  const form = document.getElementById("predict-form");
  const submitBtn = document.getElementById("submit-btn");

  const ticketEmpty = document.getElementById("ticket-empty");
  const ticketResult = document.getElementById("ticket-result");
  const ticketLoading = document.getElementById("ticket-loading");
  const ticketError = document.getElementById("ticket-error");
  const ticketErrorMsg = document.getElementById("ticket-error-msg");

  const ticketAmount = document.getElementById("ticket-amount");
  const ticketSummary = document.getElementById("ticket-summary");
  const ticketId = document.getElementById("ticket-id");
  const ticketStamp = document.getElementById("ticket-stamp");

  function showPanel(panel) {
    [ticketEmpty, ticketResult, ticketLoading, ticketError].forEach((el) => {
      el.hidden = el !== panel;
    });
  }

  function formatCurrency(value) {
    return "$" + Number(value).toLocaleString("en-US", {
      maximumFractionDigits: 0,
    });
  }

  function genderLabel(value) {
    return value === "male" ? "ذكر" : "أنثى";
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const payload = {
      gender: formData.get("gender"),
      age: formData.get("age"),
      salary: formData.get("salary"),
      debt: formData.get("debt"),
      net_worth: formData.get("net_worth"),
    };

    submitBtn.disabled = true;
    showPanel(ticketLoading);

    try {
      const res = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "حصل خطأ غير متوقع");
      }

      // restart stamp animation
      ticketStamp.style.animation = "none";
      void ticketStamp.offsetWidth;
      ticketStamp.style.animation = "";

      ticketAmount.textContent = formatCurrency(data.prediction);
      ticketId.textContent = "#" + Math.floor(100000 + Math.random() * 899999);

      ticketSummary.innerHTML = "";
      const rows = [
        ["النوع", genderLabel(payload.gender)],
        ["السن", payload.age + " سنة"],
        ["الدخل السنوي", formatCurrency(payload.salary)],
        ["مديونية البطاقة", formatCurrency(payload.debt)],
        ["صافي الثروة", formatCurrency(payload.net_worth)],
      ];
      rows.forEach(([label, value]) => {
        const li = document.createElement("li");
        li.innerHTML = `<span>${label}</span><span>${value}</span>`;
        ticketSummary.appendChild(li);
      });

      showPanel(ticketResult);
    } catch (err) {
      ticketErrorMsg.textContent = err.message || "حصل خطأ أثناء الاتصال بالسيرفر";
      showPanel(ticketError);
    } finally {
      submitBtn.disabled = false;
    }
  });
})();
