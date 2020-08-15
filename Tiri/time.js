// document.write('오늘날짜 <br>');
//     var now=new Date();
//     var y=now.getYear()+1900;
//     var m=now.getMonth()+1;
//     var d=now.getDate();
//     var week;
//             switch (dd)
//             {
//                 case 0: week='일';break;
//                 case 1: week='월';break;
//                 case 2: week='화';break;
//                 case 3: week='수';break;
//                 case 4: week='목';break;
//                 case 5: week='금';break;
//                 case 6: week='토';break;
//
//             }
//     var h=now.getHours();
//             var ap;
//             if(h>12){
//                 ap='PM저녁';
//                 h=h-12
//             }
//             else if(hour<24){
//                 ap='AM아침';
//                 h='0'+h
//             }
//     var mm=now.getMinutes();
//     if(mm>=10);
//     else
//         mm='0'+mm;
//     var s=now.getSeconds();
//     if(s>=10);
//     else
//         s='0'+s
//
//
// document.write(y+'년'+m+'월'+d+'일'+'('+week+')<br>'+ap+''+h+'시'+mm+'분'+s+'초');

function time1() {
    var today=new Date();
    document.body.innerText=today.toLocaleString();
    setTimeout("time1()",1000);
}
