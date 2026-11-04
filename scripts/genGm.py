from lib.ctl import folder


def link(ident):
    return {"type": "ccmLink", "id": ident}


def links(idents):
    return [link(ident) for ident in idents]


def buildGm():
    deviceControl = [170, 171, 172, 173]
    gm2Effects = [210, 211, 212, 213, 214, 215, 216]
    return {
        "tables": [],
        "items": [
            folder("General MIDI 1", links([200]) + [folder("Device Control", links(deviceControl))]),
            folder(
                "General MIDI 2",
                links([202])
                + [
                    folder("Device Control", links(deviceControl)),
                    folder("GM2 Effects", links(gm2Effects)),
                ],
            ),
        ],
    }
