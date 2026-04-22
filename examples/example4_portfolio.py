"""
Example 4: Portfolio and Position Management
Shows how to manage trading positions and portfolio
"""

import sys
sys.path.insert(0, '.')

from src.utils.portfolio import PortfolioManager, RiskLevel

def example_portfolio_management():
    """Example: Manage trading positions and portfolio"""
    
    print("\n" + "="*60)
    print("EXAMPLE 4: Portfolio and Position Management")
    print("="*60)
    
    # Initialize portfolio
    initial_capital = 50000
    print(f"\n[1] Creating portfolio with ${initial_capital:,.0f}")
    
    portfolio = PortfolioManager(
        initial_capital=initial_capital,
        daily_loss_limit=0.05,  # 5% daily loss limit
        max_trades_per_day=10,
        max_position_size=0.02,  # 2% per position
        risk_level=RiskLevel.MEDIUM
    )
    
    print(f"✓ Portfolio created")
    print(f"  Risk Level: MEDIUM")
    print(f"  Daily Loss Limit: 5%")
    print(f"  Max Position Size: 2%")
    
    # Add positions
    print("\n[2] Adding trading positions...")
    
    positions_data = [
        {
            'symbol': 'BTC/USDT',
            'entry_price': 45000,
            'quantity': 0.5,
            'stop_loss': 44000,
            'take_profit': 47000,
            'type': 'LONG'
        },
        {
            'symbol': 'ETH/USDT',
            'entry_price': 2500,
            'quantity': 5,
            'stop_loss': 2400,
            'take_profit': 2700,
            'type': 'LONG'
        },
        {
            'symbol': 'BNB/USDT',
            'entry_price': 600,
            'quantity': 10,
            'stop_loss': 580,
            'take_profit': 650,
            'type': 'LONG'
        }
    ]
    
    for pos in positions_data:
        success = portfolio.add_position(
            symbol=pos['symbol'],
            entry_price=pos['entry_price'],
            quantity=pos['quantity'],
            stop_loss=pos['stop_loss'],
            take_profit=pos['take_profit'],
            position_type=pos['type']
        )
        
        if success:
            print(f"  ✓ {pos['symbol']}: {pos['quantity']} @ ${pos['entry_price']}")
        else:
            print(f"  ✗ {pos['symbol']}: Failed to add position")
    
    # Display open positions
    print("\n[3] Open Positions:")
    print("-" * 60)
    
    open_positions = portfolio.get_open_positions()
    print(f"{'Symbol':<15} {'Price':>12} {'Qty':>10} {'SL':>12} {'TP':>12}")
    print("-" * 60)
    
    for pos in open_positions:
        print(f"{pos['symbol']:<15} ${pos['entry_price']:>11.2f} {pos['quantity']:>10.2f} ${pos['stop_loss']:>11.2f} ${pos['take_profit']:>11.2f}")
    
    # Get metrics
    print("\n[4] Portfolio Metrics:")
    print("-" * 60)
    
    metrics = portfolio.get_metrics()
    
    print(f"Total Capital: ${metrics.total_capital:,.2f}")
    print(f"Current Balance: ${metrics.current_balance:,.2f}")
    print(f"Used Margin: ${metrics.used_margin:,.2f}")
    print(f"Current Equity: ${metrics.equity:,.2f}")
    print(f"Return: {metrics.return_pct:.2f}%")
    print(f"Win Rate: {metrics.win_rate:.1f}%")
    print(f"Open Positions: {metrics.open_positions}")
    
    # Close some positions
    print("\n[5] Closing Positions...")
    print("-" * 60)
    
    # Close BTC position at profit
    closed_btc = portfolio.close_position('BTC/USDT', 46000, reason='TAKE_PROFIT')
    if closed_btc:
        print(f"✓ BTC/USDT closed at $46000")
        print(f"  P&L: ${closed_btc['pnl']:.2f} ({closed_btc['pnl_pct']:.2f}%)")
    
    # Close ETH position at loss
    closed_eth = portfolio.close_position('ETH/USDT', 2450, reason='STOP_LOSS')
    if closed_eth:
        print(f"✓ ETH/USDT closed at $2450")
        print(f"  P&L: ${closed_eth['pnl']:.2f} ({closed_eth['pnl_pct']:.2f}%)")
    
    # Update trailing stop for BNB
    print("\n[6] Using Trailing Stop Loss...")
    updated = portfolio.update_trailing_stop('BNB/USDT', 620, 10)
    if updated:
        print(f"✓ BNB/USDT trailing stop updated to $610")
    
    # Check stop loss and take profit
    print("\n[7] Checking Price Levels...")
    
    # Check if BNB hit SL
    bnb_hit_sl = portfolio.check_stop_loss('BNB/USDT', 570)
    bnb_hit_tp = portfolio.check_take_profit('BNB/USDT', 670)
    
    if bnb_hit_sl:
        print("⚠️  BNB/USDT would hit Stop Loss at $570")
    if bnb_hit_tp:
        print("✓ BNB/USDT would hit Take Profit at $670")
    
    # Final metrics
    print("\n[8] Final Portfolio Status:")
    print("-" * 60)
    
    final_metrics = portfolio.get_metrics()
    
    print(f"Total Trades Closed: {final_metrics.total_trades}")
    print(f"Win Rate: {final_metrics.win_rate:.1f}%")
    print(f"Total Return: {final_metrics.return_pct:.2f}%")
    print(f"Open Positions: {final_metrics.open_positions}")
    print(f"Daily P&L: ${portfolio.daily_pnl:.2f}")
    
    print("\n" + "="*60)
    print("Example 4 Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    example_portfolio_management()
