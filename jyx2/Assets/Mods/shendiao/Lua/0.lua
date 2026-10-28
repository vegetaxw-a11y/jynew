ScreenVignette(true)
Talk(0, "（娘临走时说，爹死在嘉兴的这座铁枪庙里。）")
Talk(0, "（庙里的那杆铁枪还在，人却早没了。）")
Talk(0, "（我叫杨过，字改之。娘说，盼我一辈子改过向善。）")
Talk(0, "（可我连爹娘的模样都记不清，又改谁的过？）")
Talk(0, "（庙后的破窑，如今便是我的家。）")
ScreenVignette(false)
SetFlagInt("序章开始", 1)
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
ShowMessage("序章·铁枪庙：在庙里四处走走，打听父亲的旧事。")
do return end;
