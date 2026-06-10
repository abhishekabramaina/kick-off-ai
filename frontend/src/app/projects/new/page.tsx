"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { projectsApi } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import useDrivePicker from 'react-google-drive-picker';

type Step = "input" | "analyzing" | "refinement" | "finalizing" | "complete";

interface Ambiguity {
  type: string;
  description: string;
  question_for_client: string;
}

export default function NewProject() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("input");
  const [name, setName] = useState("");
  const [rawInput, setRawInput] = useState("");
  const [projectId, setProjectId] = useState<string | null>(null);
  const [ambiguities, setAmbiguities] = useState<Ambiguity[]>([]);
  const [clarifications, setClarifications] = useState("");
  const [prd, setPrd] = useState("");
  const [loading, setLoading] = useState(false);
  const [openPicker] = useDrivePicker();

  const handleOpenPicker = () => {
    openPicker({
      clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
      developerKey: process.env.NEXT_PUBLIC_GOOGLE_API_KEY!,
      viewId: "DOCS",
      showUploadView: true,
      showUploadFolders: true,
      supportDrives: true,
      multiselect: true,
      callbackFunction: async (data) => {
        if (data.action === 'picked') {
          setLoading(true);
          try {
            // We need a project ID to ingest into. If not created, create one with a temp name.
            let currentId = projectId;
            if (!currentId) {
              const tempProject = await projectsApi.create({ name: name || "Draft Project", raw_input: "" });
              setProjectId(tempProject.id);
              setName(tempProject.name);
              currentId = tempProject.id;
            }

            for (const file of data.docs) {
              const res = await projectsApi.driveIngest(currentId!, {
                file_id: file.id,
                access_token: data.accessToken,
                file_name: file.name,
                mime_type: file.mimeType
              });
              setRawInput(prev => prev + `\n\n--- [Ingested: ${file.name}] ---\n` + res.extracted_text);
            }
          } catch (err) {
            alert("Failed to ingest from Drive");
          } finally {
            setLoading(false);
          }
        }
      },
    });
  };

  async function handleStart() {
    setLoading(true);
    try {
      const project = await projectsApi.create({ name, raw_input: rawInput });
      setProjectId(project.id);
      setStep("analyzing");
      const analysis = await projectsApi.analyze(project.id);
      setAmbiguities(analysis);
      setStep("refinement");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to start project");
    } finally {
      setLoading(false);
    }
  }

  async function handleFinalize() {
    if (!projectId) return;
    setLoading(true);
    setStep("finalizing");
    try {
      const project = await projectsApi.finalize(projectId, clarifications);
      setPrd(project.final_prd);
      setStep("complete");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to finalize PRD");
      setStep("refinement");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '2rem auto' }}>
      {step === "input" && (
        <div className="flex-col gap-4">
          <h2>New Project Kickoff</h2>
          <p className="text-muted">Paste your meeting notes or project vision below.</p>
          <div className="flex-col mt-4">
            <label>Project Name</label>
            <input 
              type="text" 
              className="card mt-4" 
              style={{ padding: '0.75rem' }}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., E-commerce App Redesign"
            />
          </div>
          <div className="flex-col mt-4">
            <div className="flex justify-between items-center">
              <label>Raw Notes / Input</label>
              <button 
                className="btn btn-outline" 
                style={{ fontSize: '0.8rem', padding: '0.25rem 0.75rem' }}
                onClick={handleOpenPicker}
                type="button"
              >
                📁 Import from Google Drive
              </button>
            </div>
            <textarea 
              className="card mt-4" 
              style={{ minHeight: '300px', padding: '0.75rem', fontFamily: 'inherit' }}
              value={rawInput}
              onChange={(e) => setRawInput(e.target.value)}
              placeholder="The client wants a mobile app for their bakery. They need a loyalty program..."
            />
          </div>
          <button 
            className="btn btn-primary mt-4" 
            disabled={!name || !rawInput || loading}
            onClick={handleStart}
          >
            {loading ? "Initializing..." : "Start AI Analysis"}
          </button>
        </div>
      )}

      {(step === "analyzing" || step === "finalizing") && (
        <div className="flex-col items-center gap-4 py-8" style={{ padding: '4rem 0' }}>
          <div className="spinner"></div> {/* Basic spinner animation could be added to CSS */}
          <h2>AI is {step === "analyzing" ? "analyzing requirements" : "generating your PRD"}...</h2>
          <p className="text-muted">This usually takes a few seconds.</p>
        </div>
      )}

      {step === "refinement" && (
        <div className="flex-col gap-4">
          <h2>Clarify Requirements</h2>
          <p className="text-muted">The AI has identified some areas that need clarification before we can generate a solid PRD.</p>
          
          <div className="flex-col gap-4 mt-4">
            {ambiguities.map((amb, i) => (
              <div key={i} className="card" style={{ borderLeft: '4px solid var(--warning)', background: '#fffbeb' }}>
                <div className="badge badge-warning mb-4">{amb.type.toUpperCase()}</div>
                <p><strong>Observation:</strong> {amb.description}</p>
                <p className="mt-4"><strong>AI Question:</strong> {amb.question_for_client}</p>
              </div>
            ))}
          </div>

          <div className="flex-col mt-4">
            <label>Your Clarifications</label>
            <textarea 
              className="card mt-4" 
              style={{ minHeight: '150px', padding: '0.75rem', fontFamily: 'inherit' }}
              value={clarifications}
              onChange={(e) => setClarifications(e.target.value)}
              placeholder="Type your answers to the AI's questions here..."
            />
          </div>

          <button className="btn btn-primary mt-4" onClick={handleFinalize} disabled={loading}>
            Generate Final PRD
          </button>
        </div>
      )}

      {step === "complete" && (
        <div className="flex-col gap-4">
          <div className="flex justify-between items-center">
            <h2>Generated PRD</h2>
            <div className="badge badge-success">FINALIZED</div>
          </div>
          <div className="card mt-4 prd-content" style={{ maxHeight: '600px', overflowY: 'auto', background: '#fcfcfc' }}>
            <ReactMarkdown>{prd}</ReactMarkdown>
          </div>
          <div className="flex gap-4 mt-4">
            <button className="btn btn-primary" onClick={() => router.push(`/projects/${projectId}/resourcing`)}>
              Proceed to Resourcing
            </button>
            <button className="btn btn-outline" onClick={() => router.push('/')}>
              Back to Dashboard
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid var(--border);
          border-top: 4px solid var(--primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .prd-content :global(h1) { font-size: 1.5rem; margin-top: 1.5rem; }
        .prd-content :global(h2) { font-size: 1.25rem; margin-top: 1.25rem; }
        .prd-content :global(ul) { margin-left: 1.5rem; margin-bottom: 1rem; }
        .prd-content :global(p) { margin-bottom: 1rem; }
      `}</style>
    </div>
  );
}
