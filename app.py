from flask import Flask, render_template, request
import pandas as pd
import textdistance
import re
from collections import Counter

app = Flask(__name__, template_folder='D:\Keyboard-Auto-Suggestion-NLP-Python-Project-main\my_template')

# Load and process the words
with open('autocorrect book.txt', 'r', encoding='utf-8') as f:
    data = f.read().lower()
    words = re.findall(r'\w+', data)
    words_freq_dict = Counter(words)

V = set(words)  # Unique words
Total = sum(words_freq_dict.values())  # Total word count
probs = {k: words_freq_dict[k] / Total for k in words_freq_dict.keys()}  # Probabilities of words

@app.route('/')
def index():
    return render_template('index.html', suggestions=None, entered_word=None)

@app.route('/suggest', methods=['POST'])
def suggest():
    keyword = request.form['keyword'].lower()
    
    if keyword:
        # Calculate Jaccard similarity for each word in the vocabulary
        similarities = [1 - textdistance.Jaccard(qval=2).distance(v, keyword) for v in words_freq_dict.keys()]
        df = pd.DataFrame.from_dict(probs, orient='index').reset_index()
        df.columns = ['Word', 'Prob']
        df['Similarity'] = similarities
        
        # Sort by Similarity first, and then by Probability
        suggestions = df.sort_values(['Similarity', 'Prob'], ascending=False)[['Word', 'Similarity']]
        
        # Get top suggestions and return
        suggestions_list = suggestions.head(10).to_dict('records')  # Limit to top 10 suggestions for efficiency
        
        # Pass the keyword (entered word) to the template along with suggestions
        return render_template('index.html', suggestions=suggestions_list, entered_word=keyword)
    
    return render_template('index.html', suggestions=None, entered_word=None)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
