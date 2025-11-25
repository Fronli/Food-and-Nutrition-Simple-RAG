import json
import numpy as np
from rag import retriever

# ======================================================
# evan_ruag buat ngecek ato eval rag modelnye!
# ======================================================

def evaluate_retriever(ground_truth_file: str, top_k: int = 5):
    """
    Evaluasi retriever menggunakan dataset ground truth
    Format JSON (list of dict):
    [
        {"question": "...", "relevant_doc": "nama dokumen yang relevan"},
        ...
    ]
    """
    with open(ground_truth_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    recall_list, precision_list, mrr_list = [], [], []

    print(f"🔍 Evaluating {len(data)} queries ...\n")

    for item in data:
        query = item["question"]
        relevant = item["relevant_doc"].lower()

        retrieved_docs = retriever.invoke(query)

        retrieved_texts = [doc.page_content.lower() for doc in retrieved_docs]

        relevant_found = [r for r in retrieved_texts if relevant in r]

        recall = 1 if relevant_found else 0
        precision = len(relevant_found) / len(retrieved_texts)

        rank = None
        for i, r in enumerate(retrieved_texts):
            if relevant in r:
                rank = i + 1
                break
        reciprocal_rank = 1 / rank if rank else 0

        recall_list.append(recall)
        precision_list.append(precision)
        mrr_list.append(reciprocal_rank)

        print(f"Q: {query}")
        print(f"→ Relevant doc: {relevant}")
        print(f"→ Retrieved top {top_k}: {[t[:80]+'...' for t in retrieved_texts[:3]]}")
        print(f"Recall@{top_k}: {recall} | Precision@{top_k}: {precision:.2f} | RR: {reciprocal_rank:.2f}\n")

    results = {
        f"Recall@{top_k}": np.mean(recall_list),
        f"Precision@{top_k}": np.mean(precision_list),
        "MRR": np.mean(mrr_list),
    }

    print("\n📊 === Evaluation Summary ===")
    for k, v in results.items():
        print(f"{k}: {v:.3f}")

    return results


if __name__ == "__main__":
   results = evaluate_retriever("rag_eval_dataset.json", top_k=5)
