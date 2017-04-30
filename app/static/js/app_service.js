//app_service.js >> Request & Response Handler - Interacts directly with the Wish List API

(function(){
    "use strict";
    
    angular
        .module('wishListApp') //Accesses the angular module wishListApp
            .factory('WishListData', WishListDataService); //Service for wishListApp created
            
    WishListDataService.$inject = ['$http'];
    
    function WishListDataService($http){
        var wishListData = {
          requestData: requestData
        };
        
        return wishListData; 
        
        //NB >> console.log(angular.toJson());
        
        function requestData(reqMethod, reqUrl, reqHeaders, reqData){
            var requestDataObj = {
                method: reqMethod,
                //url: 'https://info3180-project2-kimberlyas.c9users.io/' + reqUrl,
                url: 'https://wishlist-app-2017.herokuapp.com/' + reqUrl,
                headers: reqHeaders,
                data: reqData
            };
            
            console.log("Request >> Object:- "); console.log(requestDataObj);
            
            return $http(requestDataObj
                ).then(function(response){
                    // Callback >> Called asynchronously when the response is available
                    console.log("Response >> Body:- "); console.log(response.data); 
                    console.log("Response >> Data in Body:- "); console.log(response.data["data"]);
                    
                    return response.data["data"];
                }, function(error){
                    // Callback >> Called asynchronously if an error occurs
                    // Or server returns response with an error status
                    console.log("Response >> Error:- "); console.log(error);
                    
                    return error; //Error handler
                });
        }
    }
}());