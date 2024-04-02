# Dining Concierge Chatbot

## Introduction

Hey there! Welcome to my Dining Concierge Chatbot project. In this project, I've built a serverless, microservice-driven web application that acts as your personal dining concierge. Whether you're craving Italian in Manhattan or Japanese in Brooklyn, this chatbot has got you covered.

### 1. Frontend Deployment
I've seamlessly integrated the frontend from the cloud-hw1-starter repository into my application. This frontend provides a smooth user experience and interfaces effectively with the chatbot

### 2. API Development
I've used API Gateway to set up the /chatbot (POST) API, incorporating the provided Swagger specification. A Lambda function handles the chat operations and responds to messages.

### 3. Dining Concierge Chatbot
I created a Dining Concierge chatbot using Amazon Lex V2. It collects user preferences, such as location, cuisine, dining time, and number of people, and pushes this information to an SQS queue. Once the user confirms, it sends an email with restaurant suggestions.

### 4. Integration with Lex
The Lex chatbot is seamlessly integrated into the chat API using the AWS SDK. Messages are sent to the chatbot, and responses are relayed back to the user.

### 5. Yelp API Integration
I utilized the Yelp API to gather over 5,000 random restaurants from Manhattan. These restaurants are stored in DynamoDB, and partial information is indexed in an ElasticSearch instance. The scrupts is present in Utilities.ipynb notebook

### 6. Suggestions Module
A Lambda function acts as a queue worker, pulling messages from the SQS queue and sending restaurant suggestions via email to users. CloudWatch triggers automate this process.

### 7. Showing past suggestion
To retain previous suggestions, I store them in DynamoDB each time a suggestion is generated for the user. When the user returns, the bot checks if there are any past suggestions for the user and asks if they would like to receive them via email.


## Dining Concierge Chatbot Interaction

- **Bot**: Hi there, I'm your personal Concierge. How can I help?

- **User Input:** Hi
- **Bot:** You previously requested suggestions for Italian in Manhattan, do you want it over the email now?
- **User Input:** No
- **Bot:** No problem! Tell me how can I assist you today?
- **User Input:** Find me Indian restaurants in Manhattan
- **Bot:** Yeah Sure. I will ask some information to suggest you the dining restaurants.
- **Bot:** When do you plan to dine? Please specify the preferred date.
- **User Input:** Tomorrow
- **Bot:** What is your preferred time?
- **User Input:** 12 PM
- **Bot:** How many people will be dining with you?
- **User Input:** 5
- **Bot:** To send you the dining suggestions, could you please provide your email address?
- **User Input:** mk8XXX@nyu.edu
- **Bot:** Can I go ahead with your request for Indian restaurants in Manhattan on 2024-02-24 at 12:00 for 5?
- **User Input:** yes
- **Bot:** You’re all set. Expect my suggestions shortly! Have a good day.
- **User Input:** Thanks
- **Bot:** You’re welcome! Have a nice day.
User receives the following Email:
```

Here is your suggestions for Indian restaurants in Manhattan

| Name                     | Address                           | Rating | Reviews |
|--------------------------|-----------------------------------|--------|---------|
| Kanyakumari              | 20 E 17Th St,New York, Ny 10003   | 4.9    | 14      |
| Pippali                  | 129 E 27Th St,New York, Ny 10016  | 4.1    | 905     |
| Spice Mantra             | 1047 2Nd Ave,New York, Ny 10022   | 4.7    | 87      |
| Baazi                    | 2588 Broadway,New York, Ny 10025  | 3.9    | 75      |
| The Drunken Munkey - Ues | 338 E 92Nd St,New York, Ny 10128  | 4.3    | 1385    |

Hope you like the suggestions.
```
