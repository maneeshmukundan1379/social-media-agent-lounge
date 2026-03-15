import gradio as gr
from accounts import Account

# Initialize the account
user_account = Account("user_1", 1000.0)

def deposit(amount):
    try:
        user_account.deposit(float(amount))
        return f"Deposited: ${amount}. New balance: ${user_account.balance:.2f}"
    except ValueError as e:
        return str(e)

def withdraw(amount):
    try:
        user_account.withdraw(float(amount))
        return f"Withdrew: ${amount}. New balance: ${user_account.balance:.2f}"
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        user_account.buy_shares(symbol, int(quantity))
        return f"Bought: {quantity} shares of {symbol}. New balance: ${user_account.balance:.2f}"
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        user_account.sell_shares(symbol, int(quantity))
        return f"Sold: {quantity} shares of {symbol}. New balance: ${user_account.balance:.2f}"
    except ValueError as e:
        return str(e)

def report_holdings():
    holdings = user_account.report_holdings()
    return holdings if holdings else "No holdings."

def report_profit_or_loss():
    profit_loss = user_account.report_profit_or_loss()
    return f"Profit/Loss: ${profit_loss:.2f}"

def list_transactions():
    transactions = user_account.list_transactions()
    return transactions if transactions else "No transactions."

# Create Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("### Trading Simulation Account Management")
    
    with gr.Row():
        deposit_box = gr.Number(label="Deposit Amount")
        deposit_btn = gr.Button("Deposit")
        deposit_output = gr.Textbox(label="Deposit Result", interactive=False)

    with gr.Row():
        withdraw_box = gr.Number(label="Withdraw Amount")
        withdraw_btn = gr.Button("Withdraw")
        withdraw_output = gr.Textbox(label="Withdraw Result", interactive=False)

    with gr.Row():
        buy_symbol_box = gr.Textbox(label="Buy Stock Symbol (e.g., AAPL)")
        buy_quantity_box = gr.Number(label="Buy Quantity")
        buy_btn = gr.Button("Buy Shares")
        buy_output = gr.Textbox(label="Buy Result", interactive=False)

    with gr.Row():
        sell_symbol_box = gr.Textbox(label="Sell Stock Symbol (e.g., AAPL)")
        sell_quantity_box = gr.Number(label="Sell Quantity")
        sell_btn = gr.Button("Sell Shares")
        sell_output = gr.Textbox(label="Sell Result", interactive=False)

    report_holdings_btn = gr.Button("Report Holdings")
    holdings_output = gr.Textbox(label="Current Holdings", interactive=False)

    report_profit_btn = gr.Button("Report Profit/Loss")
    profit_output = gr.Textbox(label="Profit or Loss", interactive=False)

    transactions_btn = gr.Button("List Transactions")
    transactions_output = gr.Textbox(label="Transactions", interactive=False)

    deposit_btn.click(fn=deposit, inputs=deposit_box, outputs=deposit_output)
    withdraw_btn.click(fn=withdraw, inputs=withdraw_box, outputs=withdraw_output)
    buy_btn.click(fn=buy_shares, inputs=[buy_symbol_box, buy_quantity_box], outputs=buy_output)
    sell_btn.click(fn=sell_shares, inputs=[sell_symbol_box, sell_quantity_box], outputs=sell_output)
    report_holdings_btn.click(fn=report_holdings, outputs=holdings_output)
    report_profit_btn.click(fn=report_profit_or_loss, outputs=profit_output)
    transactions_btn.click(fn=list_transactions, outputs=transactions_output)

demo.launch()