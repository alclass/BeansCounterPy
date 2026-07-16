/* stairsteps02correction_etc */

const stairSteps = [29, 25, 24, 24, 24, 27, 22, 21, 21, 22, 21]
const STEP_HEIGHT_GOAL = 24


class Step {

  constructor(h, dh=null) {
    this.h = h;
    this.dh = dh;
  }

  increase_step(prev_step=null) {
    dh = this.h + prev_step.dh - STEP_HEIGHT_GOAL
    this.dh = dh > 0? dh : 0;
  }

  adjust(prev_step=null) {
    this.dh = this.dh - this.dh - prev_step.dh;
  }

}

const steps = stairSteps.map( step_h  => {
      new Step(
          h = step_h
      )
    }
)
console.log(steps)