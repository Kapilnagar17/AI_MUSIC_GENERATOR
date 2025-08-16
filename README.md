# 🎵 AI Music Generator

An AI-powered music generation project that creates piano-based music using **Facebook’s MusicGen small model**.  
The project comes with a **pre-built environment (`musicgen_env`)** so you don’t need to install dependencies manually.

---

## 🚀 Features
- Generate AI music based on:
  - Length of music (number of notes/codes).
  - Total time duration of generated track.
- Uses **pretrained models** (MusicGen small).
- Ready-to-use: no need to install libraries.
- Streamlit interface for easy interaction.

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **Prebuilt Virtual Environment**
- **PyTorch**
- **Transformers**
- **Facebook MusicGen**
- **Streamlit**

---

## 📂 Project Structure

AI_MUSIC_GENERATOR/
│── musicgen_env/ # Pre-built Python environment
│── data/ # Training / testing dataset
│── models/ # Pretrained & fine-tuned models
│── outputs/ # Generated music files
│── app.py # Streamlit app
│── README.md # Project documentation



---

## ⚡ Setup & Run

1. **Unzip the environment (if compressed):**
   - On **Windows**: Right-click `musicgen_env.zip` → Select **Extract All...**
   - On **Linux/Mac**: 
     ```bash
     unzip musicgen_env.zip
     ```

2. **Activate the environment:**
   - On **Windows**:
     ```bash
     musicgen_env\Scripts\activate
     ```
   - On **Linux/Mac**:
     ```bash
     source musicgen_env/bin/activate
     ```

3. **Run the project:**
   - On **Windows/Linux/Mac**:
     ```bash
     streamlit run app.py
     ```

