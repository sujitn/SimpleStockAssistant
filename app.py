import streamlit as st
from phi.assistant import Assistant
from phi.tools.yfinance import YFinanceTools
from phi.llm.groq import Groq
from pydantic import BaseModel, Field

class StockOrder(BaseModel):
    ticker: str = Field(..., title="Stock Ticker", description="Stock ticker of the company")
    quantity: int = Field(..., title="Quantity", description="Number of stocks to buy or sell")
    action: str = Field(..., title="Action", description="Buy or Sell action")
    stop_loss: float = Field(None, title="Stop Loss", description="Stop loss price for the stock")
    take_profit: float = Field(None, title="Take Profit", description="Take profit price for the stock")
    order_type: str = Field("market", title="Order Type", description="Type of order to execute")
    price: float = Field(None, title="Price", description="Price at which to execute the order")

stock_assistant = Assistant(name="Stock Analyst", llm=Groq(model="llama3-70b-8192"), tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_news=True)], role="Provides stock price, news, recommendations on companies")
order_assistant = Assistant(name="Stock Executor", llm=Groq(model="llama3-70b-8192"), role="Executes stock orders using provided information such as ticker, quantity, action, stop loss, take profit, order type and price", output_model=StockOrder)

st.title("Stock Market Sales Assistant")
st.caption("This app lets you explopre stock market price, news and recommendations using yfinance api and gives an option to execute an order")

main_assistant = Assistant(
    name = 'Stock Market Assistant',
    llm=Groq(model="llama3-70b-8192"),
    team=[stock_assistant],
    debug_mode=False,
    description="You are an Stock MarketSales Assistant tasked with execution of order on behalf of your client. You can also provide information about company stock price, news, recommendations and execute orders.",
    instructions=["Fetch stock price, news, recommendations and analysis using the stock analyst assistant. You can provide stock ticker to get the information.",
                  "Finally you can execute an order by providing stock ticker, quantity, action, stop loss, take profit, order type and price. do not forget to provide all the necessary information to execute the order. there is no execution api integrated in this app. so you can only see the order details in the chat."],
    streamlit=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = main_assistant.run(prompt, stream=False)
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})