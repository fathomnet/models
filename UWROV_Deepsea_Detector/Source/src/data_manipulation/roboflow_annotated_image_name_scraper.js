// ==UserScript==
// @name     Roboflow Annotated Image Name Scraper
// @version  1
// @include  https://app.roboflow.com/uwrov-2022-ml-challenge/*
// @grant    GM_addStyle
// ==/UserScript==


/***************************************************************************************
* DESCRIPTION:
* This is a GreaseMonkey script for Firefox
* to get the names of all Images that are "annotated" but not "approved" in Roboflow
* because for some reason Roboflow does not let us do this and it would be nice to not
* have to scrap the many hundreds of Images we already hand-labeled.
***************************************************************************************/

/**************************************************************************************************
* USAGE:
* 0) Install GreaseMonkey in Firefox: https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/
*    and then promptly disable it because you probably want to be safe and not sorry
* 1) Set NUM_IMAGES to the number of Images in the annotated set
*      - You might need to set this to more than NUM_IMAGES, sometimes it repeats Images
* 2) Copy this script into the GreaseMonkey script editor and save it
* 3) Navigate to the Annotate -> Dataset in the Roboflow project
* 4) Open the console window in Firefox Devtools
* 4) Enable GreaseMonkey and reload the page
* 5) Hit "ok" to start the roboflow scraper script
* 6) Navigate to the first image in the annotated section, and the scraper will start working!
			- NOTE: do NOT reload the page to run the script from this page! roboflow will include 
      				Images that are not in the annotated section if this page is reloaded.
* 7) Copy the last console output with all the image names when its done.
**************************************************************************************************/



// number of Images in the annotated set
// set this before the script is run
NUM_IMAGES = 800


// max time we will wait a page to load all elements
MAX_PAGE_LOAD_TIME_MS = 40000;
// time we wait between each check for image load
DELAY_TIME_MS = 400;

// slower check time for first load, because we will be navigating to the annotate page
FIRST_LOAD_DELAY_TIME_MS = 2000;


// For some reason setInterval isn't working in GreaseMonkey??
// and delay only works when used in the jank way in scrape_image_names
// maybe it works otherwise but I haven't read enough about the GreaseMonkey environment/async methods

async function delay(ms) {
  return await new Promise(resolve => setTimeout(resolve, ms));
}


function scrape_image_names() {
  loading_counter = 0;
  image_counter = 0;
  image_names = [];
  first_image = true;
  let run = async ()=>{
  	while(true) {
      if (first_image) {
        await delay(FIRST_LOAD_DELAY_TIME_MS);
      } else {
      	await delay(DELAY_TIME_MS);
      }
      forward_btn = document.querySelector('.next');
      if (forward_btn === null) {
        
        // If we've been waiting too long, abort
        // don't check it on the first image, because of the navigation time
        if (!first_image) {
					loading_counter++;
        }
        console.log(loading_counter);
        if (loading_counter > MAX_PAGE_LOAD_TIME_MS / DELAY_TIME_MS) {
          alert("WAITED TOO LONG");
          console.log("Skipped " + (NUM_IMAGES - image_counter) + " Images");
          console.log(image_names.toString());
          return;
        }
        
        // if it's still not loaded, try again
        continue;
      }
      
      
      
      image_name = document.title.split(' ')[0];
      // sometimes the name hasn't loaded
      if (!image_name.includes(".")) {
        continue;
      }
      
      
      loading_counter = 0;
      first_image = false;
      console.log(image_name);
      image_names.push(image_name);
      image_counter++;
      
      if (image_counter < NUM_IMAGES) {
        // this button doesn't take us to a new page, so we don't actually need persistent storage
      	forward_btn.click();
      } else {
        // plain array is not in easily copyable format in Firefox devtools, so we use string instead
        console.log(image_names.toString());
      	return;
      }
      
      
      
    }
  }
  run();
	
}




run_script = confirm("Start roboflow scraper?");

if (run_script) {
  // async, loops forever
  scrape_image_names();
  
  // code here runs before scrape_image_names ends
  // which is why everything is in a while loop
}

