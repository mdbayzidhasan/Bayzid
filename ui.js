/**
 * Bayzid — shared UI helpers: toasts, password visibility, form loading state.
 */
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const colors = {
    success: "bg-emerald-600",
    error: "bg-red-600",
    info: "bg-[#1E3A8A]",
  };
  const toast = document.createElement("div");
  toast.className = `toast text-white text-sm font-medium px-4 py-3 rounded-xl shadow-lg ${colors[type] || colors.info}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity .2s ease";
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

function togglePasswordVisibility(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";
  icon.textContent = isHidden ? "🙈" : "👁️";
}

function setButtonLoading(button, isLoading, loadingText = "Please wait…") {
  if (isLoading) {
    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
    button.disabled = true;
    button.classList.add("opacity-70", "cursor-not-allowed");
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
    button.classList.remove("opacity-70", "cursor-not-allowed");
  }
}

function initOtpInputs(containerId, onComplete) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const inputs = Array.from(container.querySelectorAll("input"));

  inputs.forEach((input, index) => {
    input.addEventListener("input", () => {
      input.value = input.value.replace(/[^0-9]/g, "").slice(0, 1);
      if (input.value && inputs[index + 1]) inputs[index + 1].focus();
      if (inputs.every((i) => i.value)) onComplete?.(inputs.map((i) => i.value).join(""));
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && inputs[index - 1]) {
        inputs[index - 1].focus();
      }
    });
    input.addEventListener("paste", (e) => {
      e.preventDefault();
      const digits = (e.clipboardData.getData("text") || "").replace(/[^0-9]/g, "").split("");
      inputs.forEach((inp, i) => (inp.value = digits[i] || ""));
      const lastFilled = inputs.filter((i) => i.value).length - 1;
      if (inputs[lastFilled]) inputs[lastFilled].focus();
      if (inputs.every((i) => i.value)) onComplete?.(inputs.map((i) => i.value).join(""));
    });
  });

  inputs[0]?.focus();
}

function startCountdown(elementId, seconds, onDone) {
  const el = document.getElementById(elementId);
  if (!el) return;
  let remaining = seconds;
  el.textContent = `Resend code in ${remaining}s`;
  const timer = setInterval(() => {
    remaining -= 1;
    if (remaining <= 0) {
      clearInterval(timer);
      onDone?.();
    } else {
      el.textContent = `Resend code in ${remaining}s`;
    }
  }, 1000);
}
