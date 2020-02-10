// Tung coin ico 

pragma solidity ^0.5.12;

contract tungcoin_ico {
    // Define the maximum of tungcoins for sale
    uint public max_tungcoins = 1000000;
    
    // 1$ = 1000 tungcoins
    // Define the conversion rate 
    uint public usd_to_tungcoins = 1000;
    
    // Define the number of tungcoins that have been bought
    uint public total_tungcoins_bought = 0;
    
    // Mapping the investor to equity in tungcoins and usd 
    mapping(address => uint) equity_tungcoins;
    mapping(address => uint) equity_usd;
    
    // Check if an investor can buy tungcoins
    modifier can_buy_tungcoins(uint usd_invested) {
        require(usd_invested * usd_to_tungcoins + total_tungcoins_bought <= max_tungcoins);
        _;
    }
    
    // Get the equity of an investor
    function equity_in_tungcoins(address investor) external view returns(uint){
        return equity_tungcoins[investor];
    }
    
    function equity_in_usd(address investor) external view returns(uint){
        return equity_usd[investor];
    }
    
    // Buying tungcoins
    function buy_tungcoins(address investor, uint usd_invested) external can_buy_tungcoins(usd_invested){
        uint tungcoins_bought = usd_invested * usd_to_tungcoins;
        equity_tungcoins[investor] += tungcoins_bought;
        equity_usd[investor] = equity_tungcoins[investor] / usd_to_tungcoins;
        total_tungcoins_bought += tungcoins_bought;
    }
    
    // Selling tungcoins
    function sell_tungcoins(address investor, uint tungcoins_sold) external {
        equity_tungcoins[investor] -= tungcoins_sold;
        equity_usd[investor] = equity_tungcoins[investor] / usd_to_tungcoins;
        total_tungcoins_bought -= tungcoins_sold;
    }
}