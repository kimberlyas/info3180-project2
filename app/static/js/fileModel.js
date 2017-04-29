(function(){
    "use strict";
    
    angular
        .module('wishListApp') //Accesses the angular module wishListApp
            .directive('fileModel', fileModel); //Directive for wishListApp created
        
    //fileModel.$inject = ['parse','WishListController']; //Should I have even injected the controller?!
    fileModel.$inject = ['$parse']; //Let's try without it first
   
    //function fileModel($parse, WishListController){ //-_- 
    function fileModel($parse){
        // var directive = {
        //     restrict: 'A',
        //     link: linkFunc,
        //     contoller: WishListController,
        //     controllerAs: 'wishlist'
        // }; //#Sighs guess we'll see
        
        var directive = {
            restrict: 'A',
            link: linkFunc
        };
        
        return directive; 
        
        function linkFunc(scope, element, attrs){
            console.log("Scope >> "); console.log(scope); //What is scope?!
            console.log("Element >> "); console.log(element); //What is element?!
            console.log("Attribute >> "); console.log(attrs); //What is attribute?!
            
            //console.log("Scope-WishList >> "); console.log(scope.wishlist); //Can this even be done?!
            //scope = scope.wishlist; //Legal or nah?! Lol
            
            var model = $parse(attrs.fileModel);
			var modelSetter = model.assign;

			element.bind('change', function(){
				scope.$apply(function(){
					modelSetter(scope, element[0].files[0]);
					//modelSetter(scope.wishlist, element[0].files[0]); //Legal or nah?! Lol
				})
			})
        }
    }
}());