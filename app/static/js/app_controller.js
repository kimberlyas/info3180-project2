(function(){
    "use strict";
    
    angular
        .module('wishListApp') //Accesses the angular module wishListApp
            .controller('WishListController', WishListController); //Controller for wishListApp created
        
    WishListController.$inject = ['WishListData', 'FileFormData', '$location', '$window', '$routeParams', '$route'];
   
    function WishListController(wishListData, fileFormData, $location, $window, $routeParams, $route){
        var wishlist = this; //Renames the object's self-reference this
        
        wishlist.addwish = {}; //New Wish
        wishlist.register = {}; //Register
        wishlist.login = {}; //Login
        wishlist.wishes = {}; //Wish List (Home)
        wishlist.delwish = {}; //Remove Wish
        
        // Local Storage stuffs
        // if ($window.localStorage.access_token && $window.localStorage.token_exp 
        //     && $window.localStorage.identity && $window.localStorage.user_name)
        // {  
        //     wishlist.token_name = $window.localStorage.user_name; // token holder's name
        //     wishlist.token_exp = $window.localStorage.token_exp; // token expiration
        //     wishlist.token_identity = $window.localStorage.identity; // token holder's id
        //     wishlist.token = $window.localStorage.access_token; // leh token
        // }
        wishlist.token_name = ""; // token holder's name
        wishlist.token_exp = ""; // token expiration
        wishlist.token_identity = ""; // token holder's id
        wishlist.token = ""; // leh token
        
        //NB >> console.log(angular.toJson());
        
        // Routing function
        wishlist.setRoute = function(route){
	        $location.path(route);
        };
        
        // Logout function
        wishlist.logout = function(){
           
            // Check if logged in
            if ($window.localStorage.access_token && $window.localStorage.token_exp 
                && $window.localStorage.identity && $window.localStorage.user_name)
            {
                // Remove token stored in localStorage.
                $window.localStorage.removeItem('access_token');
                $window.localStorage.removeItem('token_exp');
                $window.localStorage.removeItem('identity');
                $window.localStorage.removeItem('user_name');
                
                // Alert user
                $window.alert("You've been logged out.");
                
                // redirect user to home
                wishlist.setRoute('home');
            }
            else
            {
                // Alert user
                $window.alert("You're not logged in.");
            }
            
        };
        
        // Share funtion
        wishlist.share = function(){
            // Check for local storage stuff
            var userid = $window.localStorage.getItem('identity');
            
            var apiLnk = 'api/users/' + userid + '/shareWishlist';
            
            // Set up headers
            var headerObj = {
                'Content-Type': 'application/json', 
                'Authorization': 'Bearer ' + wishlist.token
            };
            
            // Set up data
            //ng-model >> Share Form
            var bodyObj = {
                email1: wishlist.share.email1,
                email2: wishlist.share.email2,
                email3: wishlist.share.email3,
                email4: wishlist.share.email4,
                email5: wishlist.share.email5
            };
            
            // Send data to API share feature
            
            wishListData.requestData('POST', apiLnk, headerObj, bodyObj)
            .then(
                function(data){
                    if(data.sent_to){
                        wishlist.share.emails = data["sent_to"]; //List
                        wishlist.share.message = "Wishlist successfully sent!"; //Message >> Success
                        
                        // Alert user
                        //$window.alert(wishlist.share.message);
                        
                        // Debug
                        console.log("Response >> List:- "); console.log(wishlist.share.emails);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.share.message);
                    }
                    else{
                        wishlist.share.message = "An error has occured while sending your wishlist!"; //Message >> Error
                        
                        // Alert user
                        //$window.alert(wishlist.share.message);
                        
                        // Debug
                        console.log("Response >> Message (Error):- "); console.log(wishlist.share.message);
                    }
                }
            );
            
        };
        
        //ng-click >> Search button
        wishlist.getThumbnails = function(){
            var headerObj = {
                'Content-Type': 'application/json', 
                'Authorization': 'Bearer ' + wishlist.token
            };
            
            //ng-model >> New Wish Form
            console.log(wishlist.addwish.url);
            var bodyObj = {
                url: wishlist.addwish.url
            };
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('GET', 'api/thumbnails', headerObj, bodyObj)
            .then(
                function(data){
                    if(data.thumbnails){
                        wishlist.addwish.thumbnails = data["thumbnails"]; //List
                        wishlist.addwish.message = "Thumbnails successfully retrieved from URL!"; //Message >> Success
                        
                        // Alert user
                        //$window.alert(wishlist.addwish.message);
                        
                        // Debug
                        console.log("Response >> List:- "); console.log(wishlist.addwish.thumbnails);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.addwish.message);
                    }
                    else{
                        wishlist.addwish.message = "An error has occured while retrieving thumbnails from URL!"; //Message >> Error
                        
                        // Alert user
                        //$window.alert(wishlist.addwish.message);
                        
                        // Debug
                        console.log("Response >> Message (Error):- "); console.log(wishlist.addwish.message);
                    }
                }
            );
        }; //Thumbnail Processing >> Accepts the website url to scrap images from
        
        // wishlist.postRegister = function(){
        //     var headerObj = {
        //         'Content-Type': undefined,
        //     };
            
        //     //ng-model >> Register Form
        //     var bodyObj = {
        //         email: wishlist.register.email,
        //         name: wishlist.register.name,
        //         password: wishlist.register.password,
        //         age: wishlist.register.age,
        //         gender: wishlist.register.gender,
        //         image: wishlist.register.image
        //     };
            
        //     // headerObj = JSON.stringify(headerObj);
        //     // bodyObj = JSON.stringify(bodyObj);
            
        //     console.log("Request (Header) >> Object:- "); console.log(headerObj);
        //     console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
        //     wishListData.requestData('POST', 'api/users/register', headerObj, bodyObj)
        //     .then(
        //         function(data){
        //             if(data.user){
        //                 wishlist.register.user = data["user"]; //Object
        //                 wishlist.register.message = "You have been successfully registered!"; //Message >> Success
                        
        //                 console.log("Response >> Object:- "); console.log(wishlist.register.user);
        //                 console.log("Response >> Message (Success):- "); console.log(wishlist.register.message);
                    
        //                 // Alert user
        //                 $window.alert(wishlist.register.message);
        //                 // Redirect to home
        //                 wishlist.setRoute('home');
        //             }
        //             else{
        //                 wishlist.register.message = "An error has occured while registering you!"; //Message >> Error
        //                 // Alert user
        //                 $window.alert(wishlist.register.message);
        //                 // Debug
        //                 console.log("Response >> Message (Error):- "); console.log(wishlist.register.message);
        //             }
        //         }
        //     );
        // }; //User Registration >> Accepts new user information and saves it
        
        wishlist.postLogin = function(){
            var headerObj = {
                'Content-Type': 'application/json'
            };
            
            //ng-model >> Login Form
            var bodyObj = {
                email: wishlist.login.email,
                password: wishlist.login.password
            };
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('POST', 'api/users/login', headerObj, bodyObj)
            .then(
                function(data){
                    if(data.user){
                        wishlist.login.payload = data["payload"]; //Object
                        wishlist.login.access_token = data["access_token"]; //String
                        wishlist.login.user = data["user"]; //Object
                        wishlist.login.message = "You have been successfully logged in!"; //Message >> Success
                        
                        // Display to user
                        $window.alert(wishlist.login.message);
                        // We store this token in localStorage so that subsequent API requests
                        // can use the token until it expires or is deleted.
                        $window.localStorage.setItem('access_token', wishlist.login.access_token);
                        $window.localStorage.setItem('token_exp', wishlist.login.payload.exp);
                        $window.localStorage.setItem('identity', wishlist.login.payload.identity);
                        $window.localStorage.setItem('user_name', wishlist.login.user.name);
                       
                        console.log("Response >> Object:- "); console.log(wishlist.login.payload);
                        console.log("Response >> Object:- "); console.log(wishlist.login.access_token);
                        console.log("Response >> Object:- "); console.log(wishlist.login.user);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.login.message);
                        
                        // Redirect to wishlist
                        wishlist.setRoute('wishList');
                    }
                    else{
                        wishlist.login.message = "An error has occured while logging you in!"; //Message >> Error
                        // Alert user
                        $window.alert(wishlist.login.message);
                        // Debug
                        console.log("Response >> Message (Error):- "); console.log(wishlist.login.message);
                    }
                }
            );
        }; //User Login >> Accepts login credentials
        
        // Checks if a token is valid
        wishlist.isAuthorized = function(){
            
            // Check if set
            if ($window.localStorage.access_token && $window.localStorage.token_exp 
                && $window.localStorage.identity && $window.localStorage.user_name)
            {
                
                // Check if expired
                if ($window.localStorage.token_exp < Date.now() / 1000)
                {
                    // Remove token stored in localStorage.
                    wishlist.logout();
                    
                    // Alert user to login again
                    $window.alert("Your token has expired. Please login again.");
                    
                    // Expired Token
                    return false;
                }
                
                // Store values
                wishlist.token_name = $window.localStorage.user_name; // token holder's name
                wishlist.token_exp = $window.localStorage.token_exp; // token expiration
                wishlist.token_identity = $window.localStorage.identity; // token holder's id
                wishlist.token = $window.localStorage.access_token; // leh token
                
                // Valid token
                return true;
            }
            
        };
        
        wishlist.getWishList = function(){
            
            // Check for local storage stuff
            var userid = wishlist.token_identity;
           
            var apiLnk = 'api/users/' + userid + '/wishlist';
            
            var headerObj = {
                'Content-Type': 'application/json', 
                'Authorization': 'Bearer ' + wishlist.token
            };
            
            var bodyObj = {};
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("API (Link) >> String:- "); console.log(apiLnk);
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('GET', apiLnk, headerObj, bodyObj)
            .then(
                function(data){
                    if(data.items){
                        wishlist.wishes.items = data["items"]; //List
                        
                        if(wishlist.wishes.items.length == 0){
                            wishlist.wishes.message = "Oops! Your wish list is empty! Make a wish!";
                        }
                        else{
                            wishlist.wishes.message = "Your wish list has been successfully retrieved!"; 
                        } //Message >> Success
                        
                        console.log("Response >> List:- "); console.log(wishlist.wishes.items);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.wishes.message);
                    }
                    else{
                        wishlist.wishes.message = "An error has occured while retrieving your wish list!"; //Message >> Error
                        
                        console.log("Response >> Message (Error):- "); console.log(wishlist.wishes.message);
                    }
                }
            );
        };
        
        wishlist.getPublicWishList = function(){
            
            // Check for url parameters 
            if ($routeParams.userid)
            {
                var userid = $routeParams.userid;
                wishlist.viewer = true;
             }
            
            var apiLnk = 'api/users/' + userid + '/shareWishlist';
            
            var headerObj = {
                'Content-Type': 'application/json'
                
            };
            
            var bodyObj = {};
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("API (Link) >> String:- "); console.log(apiLnk);
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('GET', apiLnk, headerObj, bodyObj)
            .then(
                function(data){
                    if(data.items){
                        wishlist.wishes.items = data["items"]; //List
                        
                        if(wishlist.wishes.items.length == 0){
                            wishlist.wishes.message = "Oops! This wish list is empty!";
                        }
                        else{
                            wishlist.wishes.message = "This wish list has been successfully retrieved!"; 
                        } //Message >> Success
                        
                        console.log("Response >> List:- "); console.log(wishlist.wishes.items);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.wishes.message);
                    }
                    else{
                        wishlist.wishes.message = "An error has occured while retrieving this wish list!"; //Message >> Error
                        
                        console.log("Response >> Message (Error):- "); console.log(wishlist.wishes.message);
                    }
                }
            );
        };
        
        wishlist.postItem = function(){
            var userid = wishlist.token_identity;
            
            var apiLnk = 'api/users/' + userid + '/wishlist';
            
            var headerObj = {
                'Content-Type': 'application/json', 
                'Authorization': 'Bearer ' + wishlist.token
            };
            
            //ng-model >> New Wish Form
            var bodyObj = {
                title: wishlist.addwish.title,
                description: wishlist.addwish.description_,
                url: wishlist.addwish.url,
                // thumbnail_url: wishlist.addwish.thumbnail_url
                thumbnail_url: wishlist.selectThumbnail = function(thumbnail){
                    wishlist.addwish.thumbnail_url = thumbnail;
                    return wishlist.addwish.thumbnail_url;
                }
            };
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("API (Link) >> String:- "); console.log(apiLnk);
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('POST', apiLnk, headerObj, bodyObj)
            .then(
                function(data){
                    if(data.item){
                        wishlist.addwish.item = data["item"]; //Object
                        wishlist.addwish.message = "Your wish has been successfully added!"; //Message >> Success
        
                        console.log("Response >> Object:- "); console.log(wishlist.addwish.item);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.addwish.message);
                        
                        // Alert user
                        $window.alert(wishlist.addwish.message);
                        // Redirect to wishlist
                        wishlist.setRoute('wishList');
                    }
                    else{
                        wishlist.addwish.message = "An error has occured while adding your new wish!"; //Message >> Error
                        // Alert user
                        //$window.alert(wishlist.addwish.message);
                        // Debug
                        console.log("Response >> Message (Error):- "); console.log(wishlist.addwish.message);
                    }
                }
            );
        };
        
        //check for != {} applicable
        wishlist.deleteItem = function(){
            var userid = wishlist.token_identity;
            var itemid = wishlist.delwish.itemid;
            
            var apiLnk = 'api/users/' + userid + '/wishlist/' + itemid;
            
            var headerObj = {
                'Content-Type': 'application/json', 
                'Authorization': 'Bearer ' + wishlist.token
            };
            
            //ng-model >> View Wish List
            var bodyObj = {
                itemid: wishlist.delwish.itemid
            };
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("API (Link) >> String:- "); console.log(apiLnk);
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('DELETE', apiLnk, headerObj, bodyObj)
            .then(
                function(data){
                    if(data.item){
                        wishlist.delwish.message = "Your wish has been successfully removed!"; //Message >> Success
                        
                        console.log("Response >> Message (Success):- "); console.log(wishlist.delwish.message);
                        // Alert user
                        $window.alert(wishlist.delwish.message);
                        // Reload page
                        $route.reload();
                    }
                }
            );
        }; 
        
        // Load user profile
        wishlist.getProfile = function(){
            
            // Check for local storage stuff
            var userid = wishlist.token_identity;
           
            var apiLnk = 'api/users/' + userid;
            
            var headerObj = {
                'Content-Type': 'application/json' 
            };
            
            var bodyObj = {};
            
            // headerObj = JSON.stringify(headerObj);
            // bodyObj = JSON.stringify(bodyObj);
            
            console.log("API (Link) >> String:- "); console.log(apiLnk);
            console.log("Request (Header) >> Object:- "); console.log(headerObj);
            console.log("Request (Body) >> Object:- "); console.log(bodyObj);
            
            wishListData.requestData('GET', apiLnk, headerObj, bodyObj)
            .then(
                function(data){
                    if(data.user){
                        wishlist.profile.user = data["user"]; //List
                        
                        wishlist.profile.message = "Your profile has been successfully retrieved!"; 
                       //Message >> Success
                        $window.alert(wishlist.profile.message);
                        console.log("Response >> User:- "); console.log(wishlist.profile.user);
                        console.log("Response >> Message (Success):- "); console.log(wishlist.profile.message);
                    }
                    else{
                        wishlist.wishes.message = "An error has occured while retrieving your profile!"; //Message >> Error
                        $window.alert(wishlist.profile.message);
                        
                        console.log("Response >> Message (Error):- "); console.log(wishlist.profile.message);
                    }
                }
            );
        };
        
    }
}());