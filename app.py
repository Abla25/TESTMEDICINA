from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Chiave segreta per la sessione

# Funzione per caricare le domande da un file CSV
def load_questions(subject):
    if subject == 'biologia':
        file_path = 'data/biologia.csv'
    elif subject == 'chimica':
        file_path = 'data/chimica.csv'
    else:
        return None
    
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Errore: File {file_path} non trovato.")
        return None
    except Exception as e:
        print(f"Errore durante il caricamento del file {file_path}: {str(e)}")
        return None

# Funzione per mescolare le risposte per una domanda
def shuffle_answers(row):
    answers = [row['Answer A'], row['Answer B'], row['Answer C'], row['Answer D'], row['Answer E']]
    random.shuffle(answers)
    return answers

# Pagina iniziale
@app.route('/')
def index():
    return render_template('index.html')

# Pagina del quiz
@app.route('/quiz', methods=['POST'])
def quiz():
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = int(request.form['num_questions'])
        
        df = load_questions(subject)
        if df is None:
            return "Errore: materia non trovata"
        
        # Estrai un numero casuale di domande
        questions = df.sample(n=num_questions).reset_index(drop=True)
        
        # Memorizza le domande e le risposte corrette per il confronto nei risultati
        questions_dict = questions.to_dict(orient='records')
        
        # Memorizza le risposte corrette in un dizionario per il confronto
        correct_answers_dict = {}
        for index, row in questions.iterrows():
            correct_answers_dict[row['Question']] = row['Answer A']
        
        # Salva il DataFrame delle domande e le risposte corrette in sessione
        session['questions'] = questions.to_dict(orient='records')
        session['correct_answers_dict'] = correct_answers_dict
        
        return render_template('quiz.html', subject=subject, questions=questions_dict)

# Pagina dei risultati
@app.route('/results', methods=['POST'])
def results():
    if request.method == 'POST':
        score = 0
        correct_answers = []
        wrong_answers = []

        # Carica il DataFrame delle domande e le risposte corrette dalla sessione
        questions = pd.DataFrame(session.get('questions'))
        correct_answers_dict = session.get('correct_answers_dict')

        # Verifica che le domande e le risposte corrette siano presenti in sessione
        if questions is None or correct_answers_dict is None:
            return redirect(url_for('index'))
        
        for index, row in questions.iterrows():
            question_text = row['Question']
            correct_answer = correct_answers_dict.get(question_text)  # Ottieni la risposta corretta dal dizionario
            selected_answer = request.form.get(f"question_{index}")
            
            if selected_answer == correct_answer:
                score += 1.5
                correct_answers.append((question_text, correct_answer))
            elif selected_answer:  # Verifica solo se è stata data una risposta diversa dalla corretta
                score -= 0.4
                wrong_answers.append((question_text, correct_answer, selected_answer))
            # Nessuna azione se selected_answer è vuoto o None
            
        # Pulizia della sessione dopo l'uso
        session.pop('questions', None)
        session.pop('correct_answers_dict', None)
        
        return render_template('results.html', score=max(score, 0), correct_answers=correct_answers, wrong_answers=wrong_answers)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
