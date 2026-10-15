(() => {
    const API_BASE_URL = (window.CAREER_COPILOT_API_URL || "http://localhost:8000").replace(/\/+$/, "");
    const tokenKey = "token";
    let isRegistering = false;

    function setMessage(element, text, type = "") {
        element.textContent = text;
        element.classList.toggle("error", type === "error");
        element.classList.toggle("success", type === "success");
    }

    async function request(path, options = {}) {
        const { auth = true, ...fetchOptions } = options;
        const headers = new Headers(fetchOptions.headers || {});
        const token = localStorage.getItem(tokenKey);
        if (auth && token) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        let response;
        try {
            response = await fetch(`${API_BASE_URL}${path}`, { ...fetchOptions, headers });
        } catch (error) {
            throw new Error("Could not reach the API. Check that the backend is running and try again.");
        }

        if (!response.ok) {
            let message = `Request failed (${response.status}).`;
            try {
                const body = await response.json();
                if (typeof body.detail === "string") {
                    message = body.detail;
                } else if (Array.isArray(body.detail)) {
                    message = body.detail.map((item) => item.msg).filter(Boolean).join(" ");
                }
            } catch {
                // Keep the HTTP status message when the response has no JSON body.
            }

            if (response.status === 401 && auth && token) {
                localStorage.removeItem(tokenKey);
                showWorkspace(false);
                setMessage(document.getElementById("auth-message"), "Your session expired. Please sign in again.", "error");
                window.dispatchEvent(new CustomEvent("career-auth-changed", { detail: { email: null } }));
            }
            throw new Error(message);
        }

        return response;
    }

    function showWorkspace(isAuthenticated, email = "") {
        document.getElementById("auth-section").hidden = isAuthenticated;
        document.getElementById("workspace").hidden = !isAuthenticated;
        document.getElementById("session-controls").hidden = !isAuthenticated;
        document.getElementById("session-email").textContent = email;
    }

    function setAuthMode(registering) {
        isRegistering = registering;
        document.getElementById("auth-heading").textContent = registering ? "Create your account" : "Welcome back";
        document.getElementById("auth-subheading").textContent = registering
            ? "A few details, then you’re ready to get moving."
            : "Sign in to pick up where you left off.";
        document.getElementById("auth-submit").innerHTML = registering
            ? 'Create account <span aria-hidden="true">→</span>'
            : 'Sign in <span aria-hidden="true">→</span>';
        document.getElementById("auth-switch-copy").textContent = registering ? "Already have an account?" : "New to Career Copilot?";
        document.getElementById("auth-switch").textContent = registering ? "Sign in" : "Create an account";
        document.getElementById("password").autocomplete = registering ? "new-password" : "current-password";
        setMessage(document.getElementById("auth-message"), "");
    }

    async function login(email, password) {
        const payload = new URLSearchParams({ username: email, password });
        const response = await request("/login", {
            method: "POST",
            body: payload,
            auth: false
        });
        const data = await response.json();
        if (!data.access_token) {
            throw new Error("The API did not return an access token.");
        }
        localStorage.setItem(tokenKey, data.access_token);
    }

    document.addEventListener("DOMContentLoaded", () => {
        const authForm = document.getElementById("auth-form");
        const authMessage = document.getElementById("auth-message");
        const authSubmit = document.getElementById("auth-submit");

        document.getElementById("auth-switch").addEventListener("click", () => setAuthMode(!isRegistering));
        document.getElementById("logout-button").addEventListener("click", () => {
            localStorage.removeItem(tokenKey);
            showWorkspace(false);
            setAuthMode(false);
            window.dispatchEvent(new CustomEvent("career-auth-changed", { detail: { email: null } }));
        });

        authForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            authSubmit.disabled = true;
            setMessage(authMessage, isRegistering ? "Creating your account…" : "Signing you in…");

            try {
                if (isRegistering) {
                    await request("/users/", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, password }),
                        auth: false
                    });
                }
                await login(email, password);
                showWorkspace(true, email);
                setMessage(authMessage, "");
                window.dispatchEvent(new CustomEvent("career-auth-changed", { detail: { email } }));
            } catch (error) {
                setMessage(authMessage, error.message, "error");
            } finally {
                authSubmit.disabled = false;
            }
        });

        async function restoreSession() {
            const token = localStorage.getItem(tokenKey);
            if (!token) {
                showWorkspace(false);
                window.dispatchEvent(new CustomEvent("career-auth-changed", { detail: { email: null } }));
                return;
            }

            try {
                const response = await request("/users/me");
                const user = await response.json();
                showWorkspace(true, user.email || "");
                window.dispatchEvent(new CustomEvent("career-auth-changed", { detail: { email: user.email || "" } }));
            } catch (error) {
                if (localStorage.getItem(tokenKey)) {
                    showWorkspace(false);
                    setMessage(authMessage, error.message, "error");
                    window.dispatchEvent(new CustomEvent("career-auth-changed", { detail: { email: null } }));
                }
            }
        }

        restoreSession();
    });

    window.CareerCopilot = {
        request,
        setMessage,
        showWorkspace
    };
})();
