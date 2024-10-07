def statements(total_fare_price, from_location, to_location, ttc):
    statement1 = f"Thank you for considering us. So your total fare becomes {total_fare_price}\n. Should we proceed find you a ride. (Yes/No) "
    statement2 = f"Hey! we got a customer.\n From:{from_location}\n To:{to_location}\n Travel time:{ttc}\n Total fare: {total_fare_price}"
    statement3 = f"Sorry! we didn't receive any response for your ride confirmation. May be you can try it later."
    return statement1, statement2, statement3
def statements1(corresponding_response_message_noplate, corresponding_response_message_phoneno, response_interval):
    statement4 = f"Your ride is confirmed.\n Vehicle No. Plate:{corresponding_response_message_noplate}\n Driver's Contact:{corresponding_response_message_phoneno}\n. Will be within {response_interval} to you."
    statement5 = f"Your ride has been cancelled.\n Thank you for considering us."
    statement6 = f"Sorry! The ride has been cancelled.\n Stay tuned we'll let you know about the new customer."
    statement7 = f"Happy Journey...!"
    statement8 = f"Sorry! no rides available at this moment"
    return statement4, statement5, statement6, statement7, statement8