
const stairSteps = [29, 25, 24, 24, 24, 27, 22, 21, 21, 22, 21]

const step = {height, climb}

const step_fn = (onStep, nextStep, targetHeight) => {
    newStep = onStep;
    newStep.height = onStep.height + onStep.climb - nextStep.height;
}
