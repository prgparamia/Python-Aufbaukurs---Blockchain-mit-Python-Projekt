


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;


import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract IceToken is ERC20 {
    constructor(uint256 initialSupply) ERC20(unicode"🍦 ICE Token", unicode"🍦ICE") {
        _mint(msg.sender, initialSupply);
    }
}

contract IceCreamDelivery  {
    address public factory;
    address public vendor;
    address public inspector;
    uint public pricePerUnit;
    uint public stock;
    
    
    IceToken public iceToken;
    uint public price;
    
    bool public confirmedByInspector;
    bool public paymentReleased;

    event IceCreamSold(address indexed vendor, uint quantity, uint totalPrice);
    event StockReplenished(uint amount);
    event PriceUpdated(uint newPrice);

    constructor(
        
        address _vendor,
        address _inspector,
        uint _initialStock,
        uint _pricePerUnit,
        address _iceTokenAddress
        
    ) payable {
        factory = msg.sender;
        vendor = _vendor;
        inspector = _inspector;
        stock = _initialStock;
        
        pricePerUnit = _pricePerUnit;
        price = msg.value;
        
        iceToken = IceToken(_iceTokenAddress);
        confirmedByInspector= false;
        paymentReleased = false;
    }
    modifier onlyOwner() {
        require(msg.sender == factory, "Only owner can perform this action.");
        _;
    }

    
    modifier onlyInspector() {
        require(msg.sender == inspector, "Only inspector can call this.");
        _;
    }

    modifier onlyVendor() {
        require(msg.sender == vendor, "Only vendor can call this.");
        _;
    }

    function buyIceCream(uint quantity, int tempCelsius) external payable {
        require(tempCelsius < 0, "Temperature must be below 0 degree to proceed.");
        require(quantity > 0, "Quantity must be greater than zero.");
        require(stock >= quantity, "Not enough stock.");
        uint totalPrice = quantity * pricePerUnit;
        require(msg.value == totalPrice, "Incorrect payment amount.");
        

        stock -= quantity;
        
        

        emit IceCreamSold(msg.sender, quantity, totalPrice);
    }

    function restock(uint amount) external onlyOwner {
        stock += amount;
        emit StockReplenished(amount);
    }

    function updatePrice(uint newPrice) external onlyOwner {
        require(newPrice > 0, "Price must be greater than zero.");
        pricePerUnit = newPrice;
        emit PriceUpdated(newPrice);
    }
    
    function getStock() external view returns (uint) {
        
        return stock;
    }
    
    function confirmDelivery() public onlyInspector {
        require(!confirmedByInspector, "Already confirmed.");
        confirmedByInspector = true;
    }

    function releasePayment() public {
        require(confirmedByInspector, "Delivery not confirmed.");
        require(!paymentReleased, "Payment already released.");
        payable(factory).transfer(price);
        paymentReleased = true;
    }

    function refundVendor() public onlyVendor {
        require(!confirmedByInspector, "Delivery already confirmed.");
        require(!paymentReleased, "Payment already released.");
        payable(vendor).transfer(price);
        paymentReleased = true;
        

    }
    function withdraw() external onlyOwner {
        payable(factory).transfer(address(this).balance);
    }



   function getContractBalance() public view returns (uint) {
        return address(this).balance;
    }

    receive() external payable {}
}


