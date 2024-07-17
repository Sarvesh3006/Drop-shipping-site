import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer



df = pd.read_csv(r'D:\myproject\scrap\envcode\Data\record1.csv')
print(df['Search'].isna().sum())
df.dropna(inplace=True)
print(len(df))
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df['Search'])

# Convert the TF-IDF matrix into a DataFrame
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

# Combine the TF-IDF DataFrame with the original DataFrame
df = pd.concat([df, tfidf_df], axis=1)
print(df)
# Drop the 'Search' column as we won't need it anymore
df = df.drop('Search', axis=1)
# Create a user-item matrix based on 'User' and TF-IDF features
df = df.groupby(['User', 'Category1'])[['Category1']].mean().reset_index()
user_item_matrix = df.pivot(index='User', columns='Category1', values=df.columns[4:])

# cosine_sim_matrix = cosine_similarity(user_item_matrix, user_item_matrix)
# cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)
#
#
# def recommend_products(user, num_recommendations=5):
#     if user not in cosine_sim_df.index:
#         return []
#
#     # Get the cosine similarity scores for the user
#     user_similarities = cosine_sim_df[user]
#
#     # Sort users by similarity in descending order
#     similar_users = user_similarities.sort_values(ascending=False)
#
#     # Exclude the current user from the recommendations
#     similar_users = similar_users.drop(user)
#
#     # Get the top similar user(s)
#     top_similar_user = similar_users.index[0]
#
#     # Find the products searched by the top similar user but not by the current user
#     recommended_products = df[df['User'] == top_similar_user][['Category', 'Subcategory']].drop_duplicates().head(num_recommendations)
#
#     return recommended_products
#
# # Example usage:
# user = 'admin'
# recommendations = recommend_products(user)
# print(recommendations)
