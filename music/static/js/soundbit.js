$(function()
{
	var albums = $(".album-img");
	albums.each(function(){
		// var albumID = $(this).attr("id");
		var audio = $(this).next()['0'];
		$(this).click(function()
		{
			if(audio["paused"])
				audio.play();
			else
				audio.pause()
		})
	})

	$(".grid").imagesLoaded(function(){
		$(".grid").masonry();
	})
})
