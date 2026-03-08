# SpeedRay — Project Structure (Instant Chest X-ray Diagnosis)

**Namespace:** SpeedRay  
**Tree view with folder/file names and purpose comments.**

```
SpeedRay/
├── README.md                          # Project overview, setup, and SpeedRay namespace
├── STRUCTURE.md                       # This file — full tree and purpose index
├── package.json                       # Node/React deps, scripts, SpeedRay app entry
├── .env.example                       # Env var templates (no secrets); Cloudinary, Auth0, etc.
├── .gitignore                         # Ignore node_modules, .env, build, __pycache__
│
├── src/                               # SpeedRay application source root
│   ├── index.tsx                      # React app entry; mounts SpeedRay root
│   ├── App.tsx                        # Top-level routes and layout for SpeedRay
│   ├── types/                         # Shared TypeScript types for SpeedRay
│   │   ├── index.ts                   # Re-exports all SpeedRay types
│   │   ├── xray.ts                    # X-ray image, study, and viewer types
│   │   ├── diagnosis.ts               # Diagnosis result, report, and RAG types
│   │   ├── pipeline.ts                # Backboard.io pipeline and step types
│   │   └── auth.ts                    # Auth0 user and session types
│   │
│   ├── components/                    # SpeedRay UI components
│   │   ├── XRayViewer/                # Chest X-ray image display and controls
│   │   │   ├── index.tsx              # XRayViewer container; Cloudinary image source
│   │   │   ├── XRayViewer.tsx         # Main viewer; zoom, pan, window/level
│   │   │   └── XRayViewer.module.css  # Styles for XRayViewer
│   │   ├── AnnotationOverlay/         # Overlay for Cloudinary annotations on X-ray
│   │   │   ├── index.tsx              # AnnotationOverlay container
│   │   │   ├── AnnotationOverlay.tsx  # Renders annotations and metadata from Cloudinary
│   │   │   └── AnnotationOverlay.module.css
│   │   ├── ReportPanel/               # Displays Gemini diagnostic report
│   │   │   ├── index.tsx
│   │   │   ├── ReportPanel.tsx        # Report text and structured findings
│   │   │   └── ReportPanel.module.css
│   │   ├── AudioExplanation/          # ElevenLabs audio explanation player
│   │   │   ├── index.tsx
│   │   │   ├── AudioExplanation.tsx   # Play/pause and waveform for explanation
│   │   │   └── AudioExplanation.module.css
│   │   ├── RiskBadge/                 # Presage risk prediction display
│   │   │   ├── index.tsx
│   │   │   ├── RiskBadge.tsx          # Risk level and confidence
│   │   │   └── RiskBadge.module.css
│   │   └── SubmissionLog/             # Solana uneditable log summary after submit
│   │       ├── index.tsx
│   │       ├── SubmissionLog.tsx      # Read-only log entry display
│   │       └── SubmissionLog.module.css
│   │
│   ├── ai_agents/                     # SpeedRay AI and model integrations
│   │   ├── TorchXRayModel/            # PyTorch XRayTorchModel anomaly detection
│   │   │   ├── index.ts               # Re-exports TorchXRayModel client
│   │   │   ├── client.ts              # API client to call Torch backend
│   │   │   └── types.ts               # Anomaly score and region types
│   │   ├── GeminiAPI/                 # Gemini deterministic diagnostic report
│   │   │   ├── index.ts               # Re-exports Gemini client
│   │   │   ├── client.ts              # Gemini API calls for report generation
│   │   │   └── types.ts               # Report schema and prompt types
│   │   ├── RAG/                       # RAG (NoSQL) with Kaggle + NHI datasets
│   │   │   ├── index.ts               # RAG service entry
│   │   │   ├── ragClient.ts           # NoSQL RAG query client
│   │   │   └── types.ts               # RAG context and citation types
│   │   ├── ElevenLabs/                # Audio explanation generation
│   │   │   ├── index.ts               # Re-exports ElevenLabs client
│   │   │   ├── client.ts              # Text-to-speech for explanation
│   │   │   └── types.ts               # Voice and audio response types
│   │   └── Presage/                   # Risk prediction
│   │       ├── index.ts               # Re-exports Presage client
│   │       ├── client.ts              # Risk prediction API client
│   │       └── types.ts               # Risk score and factor types
│   │
│   ├── pipeline/                      # Backboard.io pipeline orchestration
│   │   ├── index.ts                   # Pipeline orchestration entry
│   │   ├── orchestrator.ts            # Backboard.io pipeline definition and run
│   │   ├── steps/                     # Individual pipeline steps
│   │   │   ├── index.ts               # Re-exports all steps
│   │   │   ├── uploadAndAnnotate.ts   # Cloudinary upload + annotation
│   │   │   ├── runAnomalyDetection.ts # TorchXRayModel step
│   │   │   ├── fetchRAGContext.ts     # RAG (Kaggle/NHI) context step
│   │   │   ├── generateReport.ts      # Gemini report step
│   │   │   ├── generateAudio.ts       # ElevenLabs audio step
│   │   │   ├── runRiskPrediction.ts   # Presage risk step
│   │   │   └── submitLog.ts           # Solana uneditable log submission
│   │   └── types.ts                   # Pipeline run state and step I/O types
│   │
│   ├── prompts/                       # SpeedRay prompt templates and config
│   │   ├── index.ts                   # Re-exports prompts
│   │   ├── geminiReport.ts            # Gemini deterministic diagnostic report prompt
│   │   ├── ragSystem.ts               # RAG system prompt / instructions
│   │   └── types.ts                   # Prompt variable and config types
│   │
│   ├── storage/                       # Cloudinary and Solana storage
│   │   ├── index.ts                   # Storage service entry
│   │   ├── cloudinary.ts              # Cloudinary image upload, annotation, metadata
│   │   ├── solana.ts                  # Solana uneditable log write after submission
│   │   └── types.ts                   # Storage response and log types
│   │
│   ├── frontend/                      # Reactiv-ClipKit Lab frontend demo
│   │   ├── index.tsx                  # Frontend demo entry
│   │   ├── DemoLayout.tsx             # Demo layout and navigation
│   │   ├── demoRoutes.tsx             # Demo-specific routes
│   │   └── ClipKitIntegration.tsx     # Reactiv-ClipKit Lab integration hooks
│   │
│   ├── auth/                          # Auth0 authentication
│   │   ├── index.ts                   # Auth service entry and provider
│   │   ├── Auth0Provider.tsx          # Auth0 React provider wrapper
│   │   ├── useAuth.ts                 # useAuth hook for SpeedRay
│   │   └── types.ts                   # Auth user and token types
│   │
│   └── config/                        # SpeedRay app configuration
│       ├── index.ts                   # Config export
│       ├── env.ts                     # Env var parsing and validation
│       └── constants.ts               # App-wide constants and SpeedRay namespace
│
├── backend/                           # SpeedRay backend services
│   ├── README.md                      # Backend overview and run instructions
│   ├── requirements.txt               # Python deps: PyTorch, Cloudinary, etc.
│   ├── pyproject.toml                 # Optional Python project config for SpeedRay
│   │
│   ├── api/                           # HTTP/API layer
│   │   ├── __init__.py                # API package init
│   │   ├── main.py                    # FastAPI/Flask app entry; SpeedRay API
│   │   ├── routes/                    # API route modules
│   │   │   ├── __init__.py
│   │   │   ├── health.py              # Health check for Vultr/deployment
│   │   │   ├── upload.py              # Image upload; delegates to Cloudinary
│   │   │   ├── pipeline.py            # Trigger Backboard pipeline run
│   │   │   ├── report.py              # Fetch Gemini report
│   │   │   └── auth_callback.py       # Auth0 callback handling
│   │   └── middleware.py              # Auth0 token validation middleware
│   │
│   ├── ai_agents/                     # Backend AI agents (SpeedRay)
│   │   ├── __init__.py
│   │   ├── torch_xray_model/          # PyTorch XRayTorchModel anomaly detection
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # Model load and inference
│   │   │   ├── inference.py           # Anomaly detection inference pipeline
│   │   │   └── config.py              # Model path and device config
│   │   ├── gemini_api/                # Gemini diagnostic report (backend)
│   │   │   ├── __init__.py
│   │   │   ├── client.py              # Gemini API client for report
│   │   │   └── config.py              # API key and model config
│   │   ├── rag/                       # RAG over Kaggle + NHI (NoSQL)
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py           # NoSQL retriever for RAG
│   │   │   ├── datasets.py            # Kaggle/NHI dataset loading and index
│   │   │   └── config.py              # RAG index and connection config
│   │   ├── elevenlabs/                # ElevenLabs audio (backend)
│   │   │   ├── __init__.py
│   │   │   ├── client.py              # ElevenLabs TTS client
│   │   │   └── config.py              # API key and voice config
│   │   └── presage/                   # Presage risk prediction
│   │       ├── __init__.py
│   │       ├── client.py              # Presage risk API client
│   │       └── config.py              # Presage endpoint config
│   │
│   ├── pipeline/                      # Backboard.io pipeline (backend)
│   │   ├── __init__.py
│   │   ├── backboard_client.py        # Backboard.io orchestration client
│   │   ├── definition.py              # Pipeline DAG definition for SpeedRay
│   │   └── runners.py                 # Sync/async pipeline runners
│   │
│   ├── storage/                       # Backend storage (SpeedRay)
│   │   ├── __init__.py
│   │   ├── cloudinary_client.py       # Cloudinary upload, annotation, metadata
│   │   ├── solana_client.py           # Solana uneditable log submission
│   │   └── config.py                  # Storage credentials and endpoints
│   │
│   └── config/                        # Backend configuration
│       ├── __init__.py
│       ├── settings.py                # Pydantic/env settings for SpeedRay backend
│       └── constants.py               # Backend constants and namespace
│
├── deployment/                        # SpeedRay deployment configs
│   ├── README.md                      # Deployment overview (Vultr, Tailscale)
│   ├── vultr/                         # Vultr Serverless deployment
│   │   ├── Dockerfile                 # Image for SpeedRay backend + optional frontend
│   │   ├── serverless.yaml            # Vultr serverless function/config
│   │   └── env.example                # Env template for Vultr
│   ├── tailscale/                     # Tailscale secure demo network
│   │   ├── README.md                  # Tailscale setup for SpeedRay demo
│   │   └── acl.example.json           # Example ACL for demo access
│   └── backboard/                     # Backboard.io pipeline deployment
│       ├── pipeline.yaml              # Pipeline definition export for Backboard
│       └── README.md                  # How to deploy pipeline to Backboard.io
│
└── docs/                              # SpeedRay documentation
    ├── ARCHITECTURE.md                # High-level architecture and data flow
    ├── API.md                        # API endpoints and contracts
    └── DEMO.md                       # Reactiv-ClipKit Lab and Tailscale demo guide
```

---

## SpeedRay namespace summary

| Area            | Purpose |
|-----------------|---------|
| **components**  | XRayViewer, AnnotationOverlay, ReportPanel, AudioExplanation, RiskBadge, SubmissionLog |
| **ai_agents**   | TorchXRayModel, GeminiAPI, RAG (Kaggle/NHI), ElevenLabs, Presage |
| **pipeline**    | Backboard.io orchestration; steps: upload → anomaly → RAG → report → audio → risk → Solana log |
| **storage**     | Cloudinary (images, annotations, metadata); Solana (uneditable logs) |
| **frontend**    | Reactiv-ClipKit Lab demo layout and integration |
| **deployment**  | Vultr Serverless, Tailscale, Backboard.io |
| **auth**        | Auth0 authentication and session |

All items above are under the **SpeedRay** project namespace.
