function toggleSound(audio_elem)
{
	if (audio_elem.paused)
		audio_elem.play();
	else
		audio_elem.pause();
}

window.onload = function()
{
	var imgs = document.querySelectorAll("#albums_div img")
	for(var i = 0; i < imgs.length; i++)
	{
		(function(i){
			var audio_elem = document.getElementById(imgs[i].id + "-audio");
			imgs[i].addEventListener("click", function(){toggleSound(audio_elem);})	
		})(i);
	}	
};