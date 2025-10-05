from fastapi import FastAPI, UploadFile, File
import pandas as pd
import numpy as np
import shap
import joblib
import lightgbm as lgb
import io
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Exoplanet Detector API", description="AI модель для поиска экзопланет", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Загружаем модель при запуске (один раз)
model = joblib.load("model.pkl")

@app.get("/")
def root():
    return {"message": "FastAPI работает! Отправь CSV файл на /analyze/"}


# @app.post("/analyze/")
# async def analyze(file: UploadFile = File(...)):
#     """
#     Принимает CSV-файл с данными об экзопланетах,
#     анализирует его моделью и возвращает JSON с результатами.
#     """
#     try:
#         # --- 1. Чтение CSV из запроса ---
#         contents = await file.read()
#         df_test = pd.read_csv(io.BytesIO(contents))

#         # --- 2. Проверяем наличие нужных колонок ---
#         if len(df_test.columns) == 0:
#             return {"error": "Файл пустой или не содержит данных."}

#         # --- 3. Проверяем колонку с ID ---
#         id_col = None
#         for c in df_test.columns:
#             if "kepid" in c.lower():
#                 id_col = c
#                 break
#         if not id_col:
#             return {"error": "Не найдена колонка с kepid (идентификатором планеты)."}

#         total_objects = len(df_test)

#         # --- 4. Предсказание вероятности ---
#         train_features = model.feature_name()
#         X_test = df_test[train_features]
#         df_test["procent"] = model.predict(X_test)

#         # --- 5. Фильтрация по вероятности > 0.5 ---
#         filtered = df_test[df_test["procent"] > 0.5].copy()

#         # --- 6. Объяснение модели (XAI) ---
#         explainer = shap.TreeExplainer(model)
#         shap_values = explainer.shap_values(X_test.loc[filtered.index])
#         if isinstance(shap_values, list):
#             shap_values = shap_values[1]

#         top_features = []
#         for i in range(len(filtered)):
#             shap_importance = np.abs(shap_values[i])
#             top_idx = np.argsort(shap_importance)[-3:][::-1]
#             important_feats = X_test.columns[top_idx]
#             top_features.append(", ".join(important_feats))

#         filtered["xai"] = top_features

#         # --- 7. Создаем JSON ---
#         filtered.insert(0, "id", range(1, len(filtered) + 1))
#         result_json = filtered[[ "id", id_col, "procent", "xai" ]].to_dict(orient="records")

#         # return {"status": "ok", "count": len(result_json), "data": result_json}
#         return {"status": "ok", "total": total_objects, "count": len(result_json), "data": result_json}


#     except Exception as e:
#         return {"error": str(e)}

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import shap
import joblib
import io
import asyncio

# --- Инициализация FastAPI ---
app = FastAPI()

# --- Разрешаем CORS для фронта ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно указать ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Загружаем модель ---
model = joblib.load("model.pkl")


@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    """
    Принимает CSV-файл с данными об экзопланетах,
    анализирует его моделью и возвращает JSON с результатами.
    """
    try:
        # --- 1. Чтение CSV из запроса ---
        contents = await file.read()
        df_test = pd.read_csv(io.BytesIO(contents))

        # --- 2. Проверяем наличие данных ---
        if len(df_test.columns) == 0:
            return {"error": "Файл пустой или не содержит данных."}

        # --- 3. Поиск колонки с ID ---
        id_col = None
        for c in df_test.columns:
            if "kepid" in c.lower():
                id_col = c
                break
        if not id_col:
            return {"error": "Не найдена колонка с kepid (идентификатором планеты)."}

        total_objects = len(df_test)

        # --- 4. Предсказание вероятности ---
        train_features = model.feature_name()
        X_test = df_test[train_features]
        df_test["procent"] = model.predict(X_test)

        # --- 5. Фильтрация по вероятности > 0.5 ---
        filtered = df_test[df_test["procent"] > 0.5].copy()

        # --- 6. Ограничиваем до 100 записей ---
        # filtered = filtered.head(100)

        # --- 7. Объяснение модели (XAI) ---
        explainer = shap.TreeExplainer(model)
        shap_values = await asyncio.to_thread(explainer.shap_values, X_test.loc[filtered.index])
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        results = []
        for idx, (i, row) in enumerate(filtered.iterrows()):
            shap_importance = np.abs(shap_values[idx])
            top_idx = np.argsort(shap_importance)[-3:][::-1]
            important_feats = X_test.columns[top_idx]

            # XAI детали (признак + значение)
            xai_details = []
            for feat in important_feats:
                xai_details.append({
                    "feature": feat,
                    "value": float(row.get(feat, np.nan))
                })

            # Физические параметры планеты
            planet_info = {k: float(row.get(k, np.nan)) for k in [
                "koi_teq", "koi_insol", "koi_prad",
                "koi_period", "koi_duration",
                "koi_steff", "koi_srad", "koi_slogg"
            ] if k in df_test.columns}

            results.append({
                "id": idx + 1,
                "kepid": int(row[id_col]),
                "procent": float(row["procent"]),
                "xai": xai_details,
                "planet_info": planet_info
            })

        return {
            "status": "ok",
            "total_objects": total_objects,
            "count": len(results),
            "data": results
        }

    except Exception as e:
        return {"error": str(e)}