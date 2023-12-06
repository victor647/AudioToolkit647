function onDialogImported(audioFile)
{
    var filePath = audioFile.getAbsoluteAssetPath()   
	console.log("[LIDIO] Import as dialog " + filePath)
    var pathSplit = filePath.split('/')
    var fileName = pathSplit.pop()
    var eventName = fileName.substring(0, fileName.length - 4)
    var chapter = pathSplit.pop()
    var language = pathSplit.pop().substr(3)
    var dialogTreeFolder = eventName.substr(0, 8)   
	var eventFolder = "event:/VO/" + language + "/dialoguetree/" + chapter + "/" + dialogTreeFolder         
	var eventPath = eventFolder + "/" + eventName
	var event = studio.project.lookup(eventPath)   
	if (event) // skip if event already exists
	{ 
		console.log("Event already exists: " + eventPath) 
		return
	}
    // create event
    event = studio.project.create("Event") 
    event.name = eventName
    // put event into folder, create if not exist
    var folder = studio.project.lookup(eventFolder)           
	if (!folder)
	{
		folder = studio.project.create("Folder") 
		folder.name = dialogTreeFolder		
	}
	event.folder = folder;        
    // create track and assign audio file
    var track = event.addGroupTrack("Dialog")
    var sound = track.addSound(event.timeline, 'SingleSound', 0, audioFile.length)
    sound.audioFile = audioFile
    // assign to bank
    var bankName = "newbiepack_vo_" + language.toLowerCase()
    var bank = studio.project.lookup("bank:/" + bankName)
    if (bank)
    {
        event.relationships.banks.add(bank)
        console.log("Event assigned to bank: " + bankName)
    }
    else
        alert("Bank not found: " + bankName)
}

function postAudioFileImported( audioFile ) 
{
    var filePath = audioFile.getAbsoluteAssetPath()       
    console.log("[LIDIO] Import " + filePath)
    if (filePath.indexOf("VO_") !== -1) 
    {
        onDialogImported(audioFile);        
    }        
}

studio.project.audioFileImported.connect(postAudioFileImported);