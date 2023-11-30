from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Portfolio
from django.http import JsonResponse
from .stock_app import *
import json

@login_required
def portfolio_list(request):
    user_portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'user_portfolios': user_portfolios})

@login_required
def stock_operations(request):
    #username = temp
    #password = password
    user = request.user 
    api_key = "AT36SLG4VHPO2HVA"
    stock_list = get_user_portfolio_stocks(user)
    
    print(f"Request POST data: {request.POST}")

    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        intent = request.POST.get('intent')

        if intent == "1":#Add new stock to portfolio
            new_stock = request.POST.get('new_stock_add')
            new_stock_shares = request.POST.get('new_stock_shares')
            new_stock_price = request.POST.get('new_stock_price')
            action = add_stock_to_portfolio(user, new_stock, new_stock_shares, new_stock_price)
            if action:
                return JsonResponse({'result': f"Added {new_stock} to portfolio."})
            else:
                return JsonResponse({'result': f"Unable to Add {new_stock} to portfolio."})

        elif intent == "2":#Remove stock
            remove_stock = request.POST.get('remove_stock')
            stock_amount = request.POST.get('stock_amount')
            stock_data = get_current_stock_data(remove_stock, api_key)
            action = remove_stock_from_portfolio(user,remove_stock,stock_amount)
            if action:
                return JsonResponse({'result': f"{stock_amount} shares of {remove_stock} have been removed from portfolio."})
            else:
                return JsonResponse({'result': f"Unable to remove {stock_amount} shares of {remove_stock}"})

        elif intent == "3":#should you buy stock
            new_stock = request.POST.get('new_stock_buy')
            stock_data = get_current_stock_data(new_stock, api_key)
            decision = buy_sell_hold_logic(new_stock, stock_data)
            return JsonResponse({'result': f"Decision: {decision}"})
            
        elif intent == "4":#fetch and store stock data
            new_stock = request.POST.get('new_stock_fetch')
            fetch_and_store_stock_data(new_stock, api_key)
            return JsonResponse({'result': f"Fetched and stored data for {new_stock}."})

        elif intent == "5":#view saved stock data
            stock = request.POST.get('stock_save')
            stock_data = load_stock_data(stock)
            return JsonResponse({'user_portfolios': stock_list, 'result': f"Viewed saved stock data for {stock}."})
        
        else:
            return JsonResponse({'error': 'Not a valid input'})
    #return render(request, 'stock_operations.html', {'user_portfolios': stock_list})
    return render(request, 'stock_operations.html', context={'user_portfolios': get_user_portfolio_stocks(user)})