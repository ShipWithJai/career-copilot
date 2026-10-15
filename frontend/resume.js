(() => {
    function setMessage(id, text, type = "") {
        window.CareerCopilot.setMessage(document.getElementById(id), text, type);
    }

    function setBusy(button, busy, busyText) {
        if (busy) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.textContent = busyText;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            delete button.dataset.originalText;
        }
    }

    function makeElement(tag, className, text) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text) element.textContent = text;
        return element;
    }

    function makeJobCard(job) {
        const card = makeElement("article", "job-card");
        const top = makeElement("div", "job-card-top");
        const companyMark = makeElement("span", "company-mark", (job.company || "J").trim().slice(0, 1));
        companyMark.setAttribute("aria-hidden", "true");

        const titleBlock = makeElement("div");
        titleBlock.append(
            makeElement("h3", "job-title", job.title || "Untitled role"),
            makeElement("p", "job-company", job.company || "Company not listed")
        );
        top.append(companyMark, titleBlock);

        const location = makeElement("p", "job-location");
        location.append(makeElement("span", "", "⌖"), document.createTextNode(job.location || "Location not listed"));

        const actions = makeElement("div", "job-actions");
        const customizeButton = makeElement("button", "button button-primary", "Tailor my resume →");
        customizeButton.type = "button";
        customizeButton.addEventListener("click", () => downloadCustomizedResume(job, customizeButton, card));
        actions.append(customizeButton);

        if (job.apply_url) {
            try {
                const applyUrl = new URL(job.apply_url);
                if (applyUrl.protocol === "https:" || applyUrl.protocol === "http:") {
                    const applyLink = makeElement("a", "apply-link", "View job ↗");
                    applyLink.href = applyUrl.href;
                    applyLink.target = "_blank";
                    applyLink.rel = "noopener noreferrer";
                    actions.append(applyLink);
                }
            } catch {
                // Do not render an apply link when the API returns an invalid URL.
            }
        }

        const message = makeElement("p", "message");
        message.setAttribute("role", "status");
        message.setAttribute("aria-live", "polite");
        card.append(top, location, actions, message);
        return card;
    }

    async function downloadCustomizedResume(job, button, card) {
        const message = card.querySelector(".message");
        setBusy(button, true, "Queueing your PDF…");
        window.CareerCopilot.setMessage(message, "");

        try {
            const response = await window.CareerCopilot.request("/resumes/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ job_id: job.id })
            });
            const { task_id: taskId } = await response.json();
            if (!taskId) {
                throw new Error("The API did not return a resume-generation task ID.");
            }

            button.textContent = "Generating PDF…";
            window.CareerCopilot.setMessage(message, "Your resume is being generated. This can take a little while; keep this page open.");

            let taskResult;
            while (true) {
                await new Promise((resolve) => window.setTimeout(resolve, 1500));
                const statusResponse = await window.CareerCopilot.request(
                    `/resumes/status/${encodeURIComponent(taskId)}`
                );
                taskResult = await statusResponse.json();

                if (taskResult.status === "completed") break;
                if (taskResult.status === "failed") {
                    throw new Error(taskResult.error || "Resume generation failed.");
                }
                if (taskResult.status !== "processing") {
                    throw new Error("The API returned an unknown resume-generation status.");
                }
            }

            if (!taskResult.pdf_base64) {
                throw new Error("The API completed the task without returning a PDF.");
            }
            const pdfBytes = Uint8Array.from(atob(taskResult.pdf_base64), (character) => character.charCodeAt(0));
            const blob = new Blob([pdfBytes], { type: "application/pdf" });
            const downloadUrl = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = downloadUrl;
            link.download = `resume_job_${job.id}.pdf`;
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
            window.CareerCopilot.setMessage(message, "Your tailored resume has been downloaded.", "success");
        } catch (error) {
            window.CareerCopilot.setMessage(message, error.message, "error");
        } finally {
            setBusy(button, false);
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        const resumeForm = document.getElementById("resume-form");
        const fileInput = document.getElementById("resume-file");
        const fileName = document.getElementById("file-name");
        const resultsSection = document.getElementById("results-section");
        const jobResults = document.getElementById("job-results");

        fileInput.addEventListener("change", () => {
            fileName.textContent = fileInput.files[0]?.name || "Choose a PDF to upload";
        });

        resumeForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const submitButton = resumeForm.querySelector('button[type="submit"]');
            const file = fileInput.files[0];
            if (!file) {
                setMessage("upload-message", "Choose a PDF file before uploading.", "error");
                return;
            }
            if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
                setMessage("upload-message", "Please choose a PDF file.", "error");
                return;
            }

            const formData = new FormData();
            formData.append("title", document.getElementById("resume-title").value.trim());
            formData.append("file", file);
            setBusy(submitButton, true, "Uploading and parsing…");
            setMessage("upload-message", "Uploading your resume…");

            try {
                const response = await window.CareerCopilot.request("/resumes/upload", {
                    method: "POST",
                    body: formData
                });
                const resume = await response.json();
                setMessage("upload-message", `${resume.title} is uploaded and ready to use.`, "success");
                resumeForm.reset();
                fileName.textContent = "Choose a PDF to upload";
            } catch (error) {
                setMessage("upload-message", error.message, "error");
            } finally {
                setBusy(submitButton, false);
            }
        });

        document.getElementById("search-jobs-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const button = form.querySelector('button[type="submit"]');
            const params = new URLSearchParams({
                q: document.getElementById("search-query").value.trim(),
                limit: "5"
            });
            const location = document.getElementById("search-location").value.trim();
            if (location) params.set("location", location);

            setBusy(button, true, "Searching…");
            setMessage("search-message", "Looking for relevant opportunities…");
            resultsSection.hidden = true;

            try {
                const response = await window.CareerCopilot.request(`/semantic?${params}`);
                const jobs = await response.json();
                jobResults.replaceChildren(...jobs.map(makeJobCard));
                document.getElementById("results-count").textContent = `${jobs.length} ${jobs.length === 1 ? "role" : "roles"}`;
                resultsSection.hidden = false;
                setMessage("search-message", "");
            } catch (error) {
                jobResults.replaceChildren();
                setMessage("search-message", error.message, "error");
            } finally {
                setBusy(button, false);
            }
        });

        window.addEventListener("career-auth-changed", (event) => {
            if (!event.detail?.email) {
                resumeForm.reset();
                fileName.textContent = "Choose a PDF to upload";
                jobResults.replaceChildren();
                resultsSection.hidden = true;
                for (const id of ["upload-message", "search-message"]) {
                    setMessage(id, "");
                }
            }
        });
    });
})();
