/**
 * AI College Assistant - Auth Page Logic
 * Handles password visibility, real-time match feedback, and button loading state.
 */

// Eye SVGs
const EYE_OPEN_SVG = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
const EYE_CLOSED_SVG = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

function togglePassword(fieldId, btn) {
    const input = document.getElementById(fieldId);
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = EYE_CLOSED_SVG;
        btn.setAttribute('aria-label', 'Hide password');
    } else {
        input.type = 'password';
        btn.innerHTML = EYE_OPEN_SVG;
        btn.setAttribute('aria-label', 'Show password');
    }
}

// Real-time password match check for signup page
document.addEventListener('DOMContentLoaded', () => {
    const pwdInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const matchStatus = document.getElementById('password-match-status');
    const signupForm = document.getElementById('signup-form');

    function checkPasswordMatch() {
        if (!confirmInput || !pwdInput || !matchStatus) return;

        const p1 = pwdInput.value;
        const p2 = confirmInput.value;

        if (!p2) {
            matchStatus.style.display = 'none';
            return;
        }

        matchStatus.style.display = 'flex';
        if (p1 === p2 && p1.length >= 6) {
            matchStatus.className = 'password-match-status valid';
            matchStatus.innerHTML = `
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                Passwords match
            `;
        } else if (p1 !== p2) {
            matchStatus.className = 'password-match-status invalid';
            matchStatus.innerHTML = `
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                Passwords do not match
            `;
        }
    }

    if (confirmInput && pwdInput) {
        confirmInput.addEventListener('input', checkPasswordMatch);
        pwdInput.addEventListener('input', checkPasswordMatch);
    }

    // Attach loading state to forms on submit
    const authForms = document.querySelectorAll('form');
    authForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (form.id === 'signup-form') {
                const p1 = pwdInput ? pwdInput.value : '';
                const p2 = confirmInput ? confirmInput.value : '';
                if (p1 !== p2) {
                    e.preventDefault();
                    if (matchStatus) {
                        matchStatus.style.display = 'flex';
                        matchStatus.className = 'password-match-status invalid';
                        matchStatus.innerHTML = `
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                            Passwords do not match. Please verify.
                        `;
                    }
                    if (confirmInput) confirmInput.focus();
                    return false;
                }
            }

            const submitBtn = form.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.classList.add('is-loading');
                submitBtn.disabled = true;
                // Re-enable in 8 seconds in case of slow network
                setTimeout(() => {
                    submitBtn.classList.remove('is-loading');
                    submitBtn.disabled = false;
                }, 8000);
            }
        });
    });
});
