# AgriSense

AgriSense is a rice maturity research web application built with **Nuxt 4 and Vue 3**, a **Flask API**, and a **TensorFlow Lite MobileNetV2 model**. Upload a rice image to classify it as **Raw** (unripe) or **Ripe**, review its model probability, and keep a local prediction history.

The interface is in Indonesian. It keeps a mobile layout on every device: a centered canvas up to 480 px wide on desktop, a full-width canvas on phones, and hamburger navigation at all screen sizes. The PowerPoint-red sidebar (`#B23724`) and snow-white canvas (`#FFFAFA`) include research-method information. A floating black circular button with a white GitHub icon links to this repository. It has no visible text or dismiss button; an accessible label describes its destination.

[Source repository](https://github.com/ragraze/agrisense-webapp)

## Features

- Image selection or drag and drop, with a preview before analysis.
- Real inference using the repository's TensorFlow Lite model.
- Raw/Ripe classification, class probabilities, and a research limitation notice.
- A single results/history section at the bottom of the prediction page, storing up to 50 records in the current browser. The newest analysis opens automatically; older records can be expanded, and history can be cleared.
- Research-method section on the dashboard describing transfer learning, preprocessing, and interpretation.
- Dataset tab with counted class/split sizes, source attribution, and documented preprocessing.
- Model-evaluation page with measured test accuracy, macro/per-class precision, recall, F1, and an accessible confusion matrix.
- Loading, empty, invalid-upload, and model-unavailable states.
- Swagger UI with interactive API documentation.
- Keyboard focus indicators, drawer focus containment, Escape-to-close navigation, and reduced-motion support.
- Separate frontend/backend Dockerfiles and a Docker Compose configuration.

## Technology stack

| Layer | Technology |
| --- | --- |
| Frontend | Nuxt 4, Vue 3, TypeScript, Lucide icons |
| API | Flask, Flasgger / Swagger UI |
| Image processing | Pillow, NumPy |
| Inference | TensorFlow Lite Runtime, MobileNetV2 |
| Container runtime | Node.js 22 frontend, Python 3.11 backend with Gunicorn |

## Repository structure

```text
backend/
  app.py                  Flask routes, image validation, model inference
  requirements.txt        Python dependencies
  inference.py            Shared inference preprocessing
  evaluate.py             Offline test-split evaluation CLI
  reports/evaluation.json Reproducible evaluation results and predictions
  tests/test_api.py       API and preprocessing tests
  Dockerfile              Backend container definition
frontend/
  app/app.vue             Application views and interactions
  app/assets/css/main.css Mobile canvas and component styles
  server/api/[...path].ts  Same-origin API proxy to Flask
  nuxt.config.ts          Nuxt configuration
  package-lock.json       Locked frontend dependencies
  Dockerfile              Multi-stage frontend container definition
model/                    Original model artifacts
notebook/                 Training and experimentation notebook
tflite/                  Runtime model (see path below)
dataset/                  Training, validation, and test images
compose.yaml              Frontend and backend service definitions
DESIGN.md                 Design direction and implementation rationale
```

The runtime model is `tflite/rice_plant_model.tflite`. Keep this file available when starting the backend. The original artifacts in `model/` are not loaded by the web application.

## Requirements

- Node.js 22 and npm.
- Python 3.11 with `venv` and pip.
- Linux x86_64 for the documented TensorFlow Lite Runtime setup.
- The model file included in this project.

TensorFlow Lite Runtime wheels depend on Python version and operating system. For other platforms, use a compatible Linux environment or adapt the inference dependency before running the API.

## Local development

Run the backend and frontend in separate terminals from the repository root.

### 1. Start Flask

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py
```

The API listens on port 5000. The local Flask command starts a development server; the backend Dockerfile uses Gunicorn.

### 2. Start Nuxt

```bash
cd frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

| Resource | Local URL |
| --- | --- |
| Application | http://localhost:3000/ |
| Swagger UI | http://localhost:5000/apidocs/ |
| Swagger specification | http://localhost:5000/apispec_1.json |
| API health | http://localhost:5000/api/health |
| Model information | http://localhost:5000/api/model |
| Evaluation report | http://localhost:5000/api/evaluation |

The Nuxt development server binds to `0.0.0.0`. To open it from a phone on the same network, use the computer's reachable LAN address on port 3000 and allow that port through the local firewall. `localhost` on a phone refers to the phone itself.

### Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `NUXT_API_BASE` | `http://127.0.0.1:5000` | Server-side Flask base URL used by the Nuxt proxy |
| `EVALUATION_PATH` | `backend/reports/evaluation.json` | Offline report served by Flask |
| `MODEL_PATH` | `<repository>/tflite/rice_plant_model.tflite` | Model path used by Flask |

For example, to use a different backend address:

```bash
cd frontend
NUXT_API_BASE=http://127.0.0.1:5000 npm run dev
```

Browser requests use `/api/*` on the frontend origin. Nuxt forwards them to Flask, so no separate browser-side API URL or CORS configuration is needed for this setup. `NUXT_API_BASE` is kept on the Nuxt server.

## API usage

### Health

```bash
curl http://localhost:5000/api/health
```

```json
{"model_available": true, "status": "ok"}
```

`model_available` reports whether the file exists. It does not guarantee that the model can be loaded or invoked. Model loading is lazy and happens on the first prediction.

### Model information

```bash
curl http://localhost:5000/api/model
```

Returns the architecture, method, class names, normalization, notebook source, and model-file availability.

### Predict an image

```bash
curl -X POST http://localhost:5000/api/predict \
  -F "image=@/absolute/path/to/rice.jpg"
```

The same endpoint is available through Nuxt at `http://localhost:3000/api/predict`.

A successful response includes:

| Field | Meaning |
| --- | --- |
| `label` | `Raw` or `Ripe` |
| `title` | Indonesian class description |
| `confidence` | Probability assigned to the selected class, between 0 and 1 |
| `probabilities` | Probabilities for both classes |
| `logit` | Raw model output before sigmoid |
| `model` | Model architecture name |
| `note` | Research limitation notice |

Per-image confidence is distinct from the measured test-split accuracy described below.

### Upload limits and errors

- Formats: JPEG, PNG, or WebP, validated by decoding the uploaded image.
- Maximum request size: 8 MiB, including multipart overhead. A file near the limit can exceed the request allowance.
- Maximum image resolution: 25 megapixels.
- EXIF orientation is corrected before conversion to RGB.

| HTTP status | Meaning |
| --- | --- |
| `200` | Prediction completed |
| `400` | Missing file, invalid image, unsupported format, or excessive image resolution |
| `413` | Request exceeds the upload limit |
| `503` | Runtime/model could not complete inference |

Errors return a JSON object with an `error` message. The API does not substitute fabricated predictions when inference fails.

## Research method

The training notebook at `notebook/fix_notebook.ipynb` uses MobileNetV2 for transfer learning, with a single-output classification layer and binary cross-entropy configured with `from_logits=True`.

Inference follows the notebook's training preprocessing and label interpretation:

1. Decode the image, apply EXIF orientation, and convert it to RGB.
2. Resize it to the model's input dimensions. The supplied model uses `160 × 160 × 3`.
3. Normalize pixels using `pixel / 127.5 - 1` and create a float32 batch.
4. Invoke the TensorFlow Lite interpreter.
5. Apply sigmoid to the output logit to obtain the Ripe probability.
6. Classify a logit greater than zero as Ripe; otherwise classify it as Raw.

Interpreter access is serialized with a lock so concurrent requests do not modify the same tensor buffers simultaneously.

### Limitations

Model probability is not measured accuracy or a calibrated guarantee. Lighting, image framing, rice variety, background, and other differences from the training data can affect predictions. The application does not validate that an uploaded image actually contains rice.

A Ripe classification does not establish a harvest date. Confirm crop conditions in the field before making agricultural decisions. Reported metrics describe the bundled test split only. No probability calibration or harvest-timing evaluation is claimed.

## Data and privacy

The application does not save uploaded images to application storage or a database. Flask processes images in memory for inference. Prediction labels, probabilities, original filenames, and timestamps are stored in the browser's `localStorage`, up to 50 records; images are not included in that history.

Use **Hapus riwayat** to clear stored history. Browser/site-data removal also clears it. History belongs to the current browser and origin and is not synchronized across devices. The server has no account or authentication system. Hosting and proxy logs are outside the application's local history mechanism.

## Docker configuration

The repository provides:

- `backend/Dockerfile`: Python 3.11, API dependencies, the TFLite model, and Gunicorn.
- `frontend/Dockerfile`: Node.js 22 with separate build and runtime stages.
- `compose.yaml`: service networking and environment configuration.
- `.dockerignore`: excludes datasets, original model artifacts, caches, and Git data from the build context; the runtime TFLite model remains included.

Both Dockerfiles use the **repository root** as their build context. Compose sets `NUXT_API_BASE=http://backend:5000`, publishes the frontend on port 3000, and binds the backend to `127.0.0.1:5000` on the host. Both runtime containers use non-root users.

**Docker images have not been built and containers have not been started as part of this task, as requested.** The frontend Dockerfile contains a future production build step; writing that instruction does not execute it.

If you later choose to build and run the containers yourself:

```bash
docker compose up --build
```

To stop them:

```bash
docker compose down
```

Compose establishes service start order but does not guarantee that inference is ready before the frontend starts. The UI reports request failures and allows retrying.

## Verification

Run the backend tests from the repository root with the virtual environment activated:

```bash
python -m pytest backend/tests -q
```

Run frontend type checking:

```bash
cd frontend
npm run typecheck
```

API tests cover Swagger availability, upload validation and size limits, preprocessing, logit interpretation, and model failure. Real-model smoke tests have also exercised the prediction endpoint using one Raw image and one Ripe image from `dataset/test`. Those two-image checks are integration smoke tests; the separate evaluation below covers the complete bundled test split.


## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Frontend cannot reach the API | Start Flask; check `NUXT_API_BASE` from the Nuxt server's environment |
| Health reports `model_available: false` | Verify the TFLite file exists or set `MODEL_PATH` to an accessible file |
| Predictions return `503` | Read backend logs; verify runtime installation, model compatibility, and model path |
| TensorFlow Lite Runtime cannot be installed | Use the documented Linux/Python combination or verify wheel availability for your platform |
| Upload returns `413` | Reduce file size enough to leave room for multipart request metadata |
| History is missing | Use the same browser and origin; check whether site storage was cleared or blocked |
| Port 3000 or 5000 is occupied | Stop the conflicting service or adjust the application/service configuration |
| Phone cannot open the application | Use the host's LAN address, check network reachability, and allow port 3000 |

## Dataset attribution and references

The included dataset README identifies [Paddy on Roboflow](https://universe.roboflow.com/agrisense-dataset/paddy-o34tk) as the source, under **CC BY 4.0**. Preserve the original dataset notices when redistributing data. This dataset notice does not establish a license for all application code or model artifacts; check their applicable terms before redistribution.

- [Nuxt runtime configuration](https://nuxt.com/docs/4.x/guide/going-further/runtime-config)
- [TensorFlow Lite Interpreter](https://www.tensorflow.org/api_docs/python/tf/lite/Interpreter)
- [Flask documentation](https://flask.palletsprojects.com/)
- [Project repository](https://github.com/ragraze/agrisense-webapp)

The floating GitHub button uses the solid GitHub mark from [Simple Icons](https://github.com/simple-icons/simple-icons/blob/develop/icons/github.svg). GitHub branding remains subject to its applicable trademark guidelines.

## Model evaluation

Open **Evaluasi model** in the hamburger menu. The page loads a saved report from `GET /api/evaluation`; it does not run inference on every page visit. The JSON download includes per-image labels and probabilities for auditing.

The supplied model was evaluated on all **189 images** in `dataset/test`: **88 Raw** and **101 Ripe**, with **0 skipped**. Results from the saved report:

| Metric | Result |
| --- | --- |
| Accuracy | 95.24% (180 / 189 correct) |
| Macro precision | 95.17% |
| Macro recall | 95.33% |
| Macro F1 | 95.22% |

Confusion matrix (rows are ground-truth folder labels; columns are predictions):

| Actual / Predicted | Raw | Ripe |
| --- | --- | --- |
| Raw | 85 | 3 |
| Ripe | 6 | 95 |

These results use the exact same inference function as the prediction endpoint. Macro metrics are the unweighted average of the two class metrics. Undefined precision/recall/F1 denominators produce zero. Metric definitions follow the [scikit-learn classification metrics conventions](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics); the implementation uses direct counts without adding a scikit-learn runtime dependency.

### Reproduce the report

With Python dependencies installed, run from the repository root:

```bash
python backend/evaluate.py
```

Optional paths:

```bash
python backend/evaluate.py \
  --model tflite/rice_plant_model.tflite \
  --dataset dataset \
  --output backend/reports/evaluation.json
```

The dataset directory must contain labeled `test/Raw` and `test/Ripe` images. Its `train` and `valid` folders are used for exact-byte overlap checks if present. The command runs inference without retraining, fails on unreadable test images rather than silently skipping them, and atomically replaces the report only after a successful evaluation. Run it again when the model or test data changes.

The report records a UTC timestamp, input shape, threshold, preprocessing, model SHA-256, dataset manifest SHA-256, class support, confusion matrix, metrics, and per-image predictions. The API checks the active model hash before serving it: a missing report returns `404`, a changed model returns `409`, and an unreadable model/report returns `503`. The API does not re-check the test dataset on each request; that dataset is intentionally excluded from Docker images. The generated report is included by the backend Dockerfile's existing `COPY backend/` instruction.

### Interpretation limits

No exact-byte overlap was found between the test images and the provided training/validation images. This does **not** establish independent splits: resized/augmented versions and adjacent video frames can differ at the byte level. Labels follow folder names and have not been independently audited. The test results must not be presented as field accuracy, generalization to unseen farms, or a recommendation for harvest timing.

## License

The application code is licensed under the [MIT License](LICENSE), copyright © 2026 Ragraze. Dataset files retain their separate CC BY 4.0 license and attribution requirements. This MIT license does not relicense third-party dependencies or model artifacts; their applicable terms remain separate.

## Dataset inventory

The **Dataset** tab shows 989 images: 488 Raw and 501 Ripe. The split counts are 600 training, 200 validation, and 189 test images. Counts come from the local project files; source metadata comes from the included dataset READMEs.

`GET /api/dataset` returns the saved inventory in `backend/reports/dataset.json`. Regenerate it after changing image files:

```bash
python backend/dataset_report.py
```

The command supports `--dataset` and `--output` paths. It counts JPEG, PNG, and WebP files under the six split/class folders and fails if a required folder is missing. Counting files is not a label or image-content audit. The page shows the inventory timestamp, the CC BY 4.0 source attribution, and the distinction between the export resize (640 × 640) and model input resize (160 × 160).

The saved inventory is included in the backend image without copying the dataset itself. A missing inventory returns HTTP 404 and an unreadable inventory returns HTTP 503. The UI provides loading/error states and a retry action. Dataset content is not re-scanned on each API request.
