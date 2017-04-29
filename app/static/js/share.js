// Share Controller [CHANGED TO SHARE FUNCTION IN WishListApp]
angular
    .module('wishListApp')
        .controller('ShareController', ['$scope','$log','$http','$window', 
            function($scope,$log,$http,$window) {
		
		        $scope.email1 = "";
                $scope.email2 = "";
                $scope.email3 = "";
                $scope.email4 = "";
                $scope.email5 = "";
        
                $scope.submit = function() {
        	        if ($scope.email1 || $scope.email2 || $scope.email3 || $scope.email4 || $scope.email5) 
        	        {
        	            // Get user ID from local storage
        		        var userid= $window.localStorage.getItem('identity');
        		        
        		        $log.log($scope.email1);
        		        $log.log($scope.email2);
        		        $log.log($scope.email3);
        		        $log.log($scope.email4);
        		        $log.log($scope.email5);
        		        
        		        // Send data to API share feature
        		        $http.post('/api/share/'+ userid +'/shareWishlist', 
        		                   {email1: $scope.email1, 
        		                    email2: $scope.email2 , 
        		                    email3: $scope.email3, 
        		                    email4: $scope.email4, 
        		                    email5:$scope.email5})
        		        .success(function (data) {
        		                    // Check message field
        			                if (data.message == "Success"){
        			                    // Alert?
        				                $window.alert('Wishlist Successfully Shared');
        				                $log.log(data);
        				
        			                }else if(data.message != "Success"){
        				                $log.log(data);
        			                }
        			
        		        })
        		        .error(function(error) {
        			            $log.log(error);
        			            $window.alert("Failed to Send");
        			
        		});
        		
        	};
        	
        };
	
}
]);

// CHANGE TEMPLATE TAGS ANGULARJS USES SO WE DONT HAVE TO USE THE {% raw %} TAGS
// $interpolateProvider.startSymbol('//');
// $interpolateProvider.endSymbol('//');