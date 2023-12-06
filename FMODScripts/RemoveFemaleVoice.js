studio.menu.addMenuItem({
    name: "LIDIO\\Remove duplicated female voice",
    execute: function()
    {
        studio.window.browserSelection().forEach(
            function(eventFemale)
            {
                var eventPathFemale = eventFemale.getPath()
                if (eventPathFemale.indexOf("femaleAvatar") === -1)
                    return
                // get sound from female event
                if (eventFemale.groupTracks.length < 1)
                    return
                var trackFemale = eventFemale.groupTracks[0]
                if (trackFemale.modules.length < 1)
                    return
                var soundFemale = trackFemale.modules[0]
                if (!soundFemale)
                    return
                // get male event
                var eventPathMale = eventPathFemale.replace("female", "male")
                var eventMale = studio.project.lookup(eventPathMale)
                if (!eventMale)
                    return
                // get sound from male event
                if (eventMale.groupTracks.length < 1)
                    return
                var trackMale = eventMale.groupTracks[0]
                if (trackMale.modules.length < 1)
                    return
                var soundMale = trackMale.modules[0]
                // only replace with reference if audio file duration equals
                if (!soundMale)
                    return
                if (soundMale.length !== soundFemale.length)
                {
                    console.log("Female has unique voice on " + eventPathFemale)
                    return
                }
                studio.project.deleteObject(soundFemale.audioFile)
                studio.project.deleteObject(soundFemale)
                // addSound will create an empty nested event. Remove it after replaced with male event
                var eventSound = trackFemale.addSound(eventFemale.timeline, 'EventSound', 0, soundFemale.length)
                var nestedEvent = eventSound.event
                eventSound.event = eventMale
                studio.project.deleteObject(nestedEvent)
                console.log("Successfully removed female voice from " + eventPathFemale)
            })
    }
});

