// /var/www/html/smart/static/js/tohtml.js
(function(global){
  function toHTML(n) {
    function r(n) {
      var r = n.charAt(0), e = n.charAt(n.length - 1);
      return -1 !== r.search(/('|\")/) && r === e ? n.substr(1, n.length - 2) : n;
    }
    var e = n.split(/(\s|\(|\)|'[^']*'|\"[^\"]*\")/).filter(function(n) {
      return "" !== n && " " !== n;
    });
    (function(n){
      for (var r=0,e=0,t=n.entries(); e<t.length; e++){
        var i=t[e], s=i[0], o=i[1];
        if ("("===o) r++; else if (")"===o && --r<0) throw new Error("Unexpected closing parentheses: "+n.slice(0,s).join(" "));
      }
      if (0!==r) throw new Error("Missing closing parentheses: "+n.join(" "));
    })(e);
    (function(n){
      for (var r=0,e=n.entries(); r<e.length; r++){
        var t=e[r], i=t[0], s=t[1];
        if (i>0 && "("===n[i-1] && ")"===s) throw new Error("Expression contains empty content: "+n.slice(0,i).join(" "));
      }
    })(e);
    return (function n(e){
      for (var t=[], i=[], s="", o=e.shift(); o && ")"!==o; ){
        if ("("===o) s ? (e.unshift(o), t.push(n(e))) : s = o = e.shift();
        else if (":"===o[0]) { var f=o.substring(1), h=r(e.shift()); i.push({key:f, value:h}); }
        else t.push(r(o));
        o=e.shift();
      }
      return ["<"+s+(i.length?" ":"")+i.map(function(n){return n.key+'=\"'+n.value+'\"'}).join(" ")+">", t.join(""), "</"+s+">"];
    })(e).join("");
  }
  global.toHTML = toHTML;
})(window);
