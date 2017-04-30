//index.js >> Configuration the angular module

(function(){
    "use strict";
    
    angular
        .module('wishListApp', ['ngRoute']) //Sets the angular module wishListApp
            .config(function($routeProvider){
        	    $routeProvider
        	        // route for the register page
        	        .when('/register', {
        	            templateUrl: 'static/partials/register.html',
        	            controller: 'WishListController'
        	        })
        	        
        	        // route for the add wish page
        	        .when('/add', {
        	            templateUrl: 'static/partials/add_wish.html',
        	            controller: 'WishListController',
        	            resolve:{
        	            	authRequired : isLoggedIn
        	            }
        	        })
        	        
        	        // route for the user profile page
        	        .when('/profile', {
        	            templateUrl: 'static/partials/profile.html',
        	            controller: 'WishListController',
        	            resolve:{
        	            	authRequired : isLoggedIn
        	            }
        	        })
        	        
        	        // route for the wishlist page
        	        .when('/wishList', {
        	            templateUrl: 'static/partials/wishlist.html',
        	            controller: 'WishListController',
        	            resolve:{
        	            	authRequired : isLoggedIn
        	            }
        	         })
        	        
        	        // route for the share page [GEORGIA]
        	        .when('/share', {
        	            templateUrl: 'static/partials/share.html',
        	            controller: 'WishListController',
        	            resolve:{
        	            	authRequired : isLoggedIn
        	            }
        	        })
        	        
        	        // route for the shared wishlist page [GEORGIA]
        	        .when('/wishList/:userid', {
        	            templateUrl: 'static/partials/publicWishlist.html',
        	            controller: 'WishListController'
        	        })
        	        
        	        //route for the home page
        	        .otherwise( { 
        	            redirectTo:'/home',
        	            templateUrl: 'static/partials/home.html',
        	            controller: 'WishListController'
        	        });
        	}
	);
	
	function isLoggedIn($window, $location){
		// Check if token is saved
		if ($window.localStorage.getItem('access_token'))
		{
			// Get expiration time of token
			var token_exp = new Date($window.localStorage.getItem('token_exp')).getTime();
			
			// Check if token has expired
            if (Date.now() > token_exp)
            {
                // Debug    
                console.log('token expired');
                    
                // Remove token stored in localStorage.
                $window.localStorage.removeItem('access_token');
                $window.localStorage.removeItem('token_exp');
                $window.localStorage.removeItem('identity');
                $window.localStorage.removeItem('user_name');
                    
                // Alert user to login again
                $window.alert("Your token has expired. Please login again.");
                
                // Redirect to home page
				$location.path('/home');
                    
                // Expired Token
                return false;
            }
            
            // Valid token
			return true;
		}
		else
		{
			// Debug
			console.log('Unauthorized access >> re-routing');
			// Redirect to home page
			$location.path('/home');
		}
	} // User must be authorized to view this page
}());





// 	var wishListApp = angular
// 	                        .module('wishListApp', ['ngRoute']); //Sets its name to wishListApp and includes ngRoute for all our routing needs
	
// 	// configure our routes
// 	wishListApp.config(function($routeProvider)
// 	{
// 	    $routeProvider
	        
// 	        // route for the register page
// 	        .when('/register', {
// 	            templateUrl: 'static/partials/register.html',
// 	            controller: 'WishListController'
// 	        })
	        
// 	        // route for the add wish page
// 	        .when('/add', {
// 	            templateUrl: 'static/partials/add_wish.html',
// 	            controller: 'WishListController',
// 	            resolve:{
// 	            	authRequired : isLoggedIn
// 	            }
// 	        })
	        
// 	        // // route for the user profile page
// 	        // .when('/profile', {
// 	        //     templateUrl: 'static/partials/profile.html',
// 	        //     controller: 'WishListController',
// 	        //     resolve:{
// 	        //    	authRequired : isLoggedIn
// 	        //    }
// 	        // })
	        
// 	        // route for the wishlist page
// 	        .when('/wishList', {
// 	            templateUrl: 'static/partials/wishlist.html',
// 	            controller: 'WishListController',
// 	            resolve:{
// 	            	authRequired : isLoggedIn
// 	            }
// 	         })
	        
// 	        // route for the share page [GEORGIA]
// 	        .when('/share', {
// 	            templateUrl: 'static/partials/share.html',
// 	            controller: 'ShareController',
// 	            resolve:{
// 	            	authRequired : isLoggedIn
// 	            }
// 	        })
	        
// 	        //route for the home page
// 	        .otherwise( { 
// 	            redirectTo:'/home',
// 	            templateUrl: 'static/partials/home.html',
// 	            controller: 'WishListController'
// 	        });
// 	});
