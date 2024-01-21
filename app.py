from flask import Flask,request
from flask import render_template
import pickle
import os
import pandas
import numpy as np
# popular_df = pickle.load('pickle\popular.pkl','rb')

# pickle files needed for item-based-filtering
# Get the absolute path to the pickled file
file_path = os.path.join(os.path.dirname(__file__), 'pickle', 'popular.pkl')
# Load the pickled file
with open(file_path, 'rb') as file:
    popular_df = pickle.load(file)

pt = pickle.load(open('pickle/pt.pkl','rb'))
similarity_scores = pickle.load(open('pickle/similarity_scores.pkl','rb'))
books = pickle.load(open('pickle/books.pkl','rb'))


#pickles file needed for user-based-filtering
pt_user = pickle.load(open('pickle/pt_user.pkl','rb'))
user_similarity = pickle.load(open('pickle/user_similarity.pkl','rb'))
df_ratings_name = pickle.load(open('pickle/df_ratings_name.pkl','rb'))

# finding the similar user_id when the user is using recommendation through user-based-filtering
def find_similar_user(user_id):
    try:
        print('index found')
        index = np.where(pt_user.index==user_id)[0][0]
    except:
        return render_template('index_error.html')
    score = user_similarity[index]
    index_score = list(enumerate(score))
    top_users = sorted(index_score,key=lambda x:x[1],reverse=True)[1:6]
    
    similar_users = []
    for i in top_users:
        similar_users.append(pt_user.index[i[0]])
    
    return similar_users

# recommend the top books from each users
def recommend_books(users):
    books=[]
    for i in users:
        temp_df = df_ratings_name[df_ratings_name['User-ID']==i]
        max_ratings = temp_df['Book-Rating'].max()
        top_preference = temp_df[temp_df['Book-Rating']==max_ratings].iloc[0]
        cols = list(top_preference[['Book-Title','Book-Author','Year-Of-Publication','Image-URL-M']].values)
        books.append(cols)
        
    return books
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           book_titles =  list(popular_df['Book-Title'].values),
                           authors = list(popular_df['Book-Author'].values),
                           publication_date = list(popular_df['Year-Of-Publication'].values),
                           ratings = list(popular_df['avg-rating']),
                           images = list(popular_df['Image-URL-M']),
                           num_ratings = list(popular_df['num-rating'])
                          )

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/recommended_books',methods=['post'])
def recommended_book():
    user_input = request.form.get('user_input')
    try:
        index = np.where(pt.index==user_input)[0][0]
    except:
        return render_template('index_error.html')
    score = similarity_scores[index]
    index_score = list(enumerate(score))
    top_books = sorted(index_score,key=lambda x:x[1],reverse = True)[1:6]
    
    data = []
    for i in top_books:
        book_info = []
        temp_df = books[books['Book-Title']==pt.index[i[0]]]
        # same books might have the different year of publication and different ISBN, but we only need one book
        temp_df = temp_df.drop_duplicates('Book-Title')
        
        book_info.append(temp_df['Book-Title'].values[0])
        book_info.append(temp_df['Book-Author'].values[0])
        book_info.append(temp_df['Year-Of-Publication'].values[0])
        book_info.append(temp_df['Image-URL-M'].values[0])
        
        data.append(book_info)

    return render_template('recommend.html',data=data)
@app.route('/similar_user')
def user_based_recommend():
    return render_template('recommend_user_based.html')

@app.route('/recommend_book_user',methods=['post'])
def recommend_based_user():
    user_input = request.form.get('user_input')
    similar_users = find_similar_user(int(user_input))
    print(similar_users)
    data = recommend_books(similar_users)

    return render_template('recommend_user_based.html',data=data)

if __name__=='__main__':
    app.run(debug=True)
