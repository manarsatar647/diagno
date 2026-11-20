"""منطق دياجنو بدون واجهة (قابل للاختبار)."""
import json, os, numpy as np, pandas as pd, joblib

class Diagno:
    def __init__(self, model_path="diagno_model.joblib", content_path="data/content_ar.json",
                 data_path="data/clean_wide.csv"):
        try:
            b = joblib.load(model_path)
            self.model, self.symptoms, self.classes, self.theta = b["model"], b["symptoms"], b["classes"], b["theta"]
        except Exception:
            self._train(data_path)   # إذا الملف غير موجود أو إصدار المكتبات مختلف: ندرّب النموذج مباشرة
        c = json.load(open(content_path, encoding="utf-8"))
        self.sym_ar = {s["symptom"]: s["label_ar"] for s in c["symptoms"]}
        self.dis = {d["name"]: d for d in c["diseases"]}
        self.emergency = set(c["emergency_symptoms"])
        self.idx = {s: i for i, s in enumerate(self.symptoms)}

    def vector(self, selected):
        v = np.zeros((1, len(self.symptoms)))
        for s in selected: v[0, self.idx[s]] = 1
        return v

    def predict(self, selected, k=3):
        p = self.model.predict_proba(self.vector(selected))[0]
        return [(self.classes[i], float(p[i])) for i in np.argsort(-p)[:k]]

    def next_questions(self, selected, n=5):
        """أعراض إضافية مقترحة (أعلى Information Gain) بعد الأعراض المحددة."""
        post = self.model.predict_proba(self.vector(selected))[0]
        th = self.theta
        H = lambda P: -(P * np.log2(P + 1e-12)).sum(0)
        p1 = post @ th
        P1 = post[:, None] * th / np.clip(p1, 1e-12, None)
        P0 = post[:, None] * (1 - th) / np.clip(1 - p1, 1e-12, None)
        ig = H(post) - (p1 * H(P1) + (1 - p1) * H(P0))
        ig[[self.idx[s] for s in selected]] = -1
        return [self.symptoms[i] for i in np.argsort(-ig)[:n]]

    def emergency_hits(self, selected):
        return [s for s in selected if s in self.emergency]

    def _train(self, data_path):
        from sklearn.naive_bayes import BernoulliNB
        rng = np.random.default_rng(0)
        df = pd.read_csv(data_path)
        self.symptoms = [c for c in df.columns if c != "disease"]
        X, y = df[self.symptoms].values, df["disease"].values

        def corrupt(Xm, p_drop, n_false):
            Xc = Xm.copy()
            for i in range(len(Xc)):
                on = np.flatnonzero(Xc[i]); drop = on[rng.random(len(on)) < p_drop]
                if len(drop) >= len(on): drop = drop[:-1]
                Xc[i, drop] = 0
                if n_false:
                    off = np.flatnonzero(Xc[i] == 0); Xc[i, rng.choice(off, n_false, replace=False)] = 1
            return Xc
        Xs, ys = [X], [y]
        for _ in range(15):
            Xs.append(corrupt(X, rng.uniform(0.1, 0.6), int(rng.integers(0, 2)))); ys.append(y)
        self.model = BernoulliNB().fit(np.vstack(Xs), np.concatenate(ys))
        self.classes = list(self.model.classes_)
        self.theta = np.vstack([(X[y == c].sum(0) + .5) / ((y == c).sum() + 1) for c in self.classes])
