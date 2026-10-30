ScreenVignette(true)
Talk(0, "（娘临走时说，爹死在嘉兴的这座铁枪庙里。）", EXPR.think)
Talk(0, "（庙里的那杆铁枪还在，人却早没了。）", EXPR.think)
Talk(0, "（我叫杨过，字改之。娘说，盼我一辈子改过向善。）", EXPR.think)
Talk(0, "（可我连爹娘的模样都记不清，又改谁的过？）", EXPR.think)
Talk(0, "（庙后的破窑，如今便是我的家。）", EXPR.think)
ScreenVignette(false)
SetFlagInt("序章开始", 1)
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
Talk(0, "（<color=#FF0000>庙里</color>还有几位香客。爹的旧事，或许有人记得。）", EXPR.think)
do return end;
