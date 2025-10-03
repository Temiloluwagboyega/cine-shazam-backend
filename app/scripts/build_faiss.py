from app.services.faiss_builder import build_faiss

if __name__ == "__main__":
    # fetch_size controls how many docs we load from Mongo per round
    # batch_size controls encoding sub-batch inside model
    build_faiss(batch_size=256, fetch_size=1000)
