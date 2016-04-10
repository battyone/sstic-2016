Github
======

L'ensemble du code que j'ai écrit pour le challenge ainsi que les fichiers ayant servis à générer ce document Markdown-\LaTeX{} seront disponibles à l'adresse \url{https://github.com/fishilico/sstic-2016} une fois le challenge terminé.

Donner les clés aux gardes par copier-coller
============================================

Dans le jeu du challenge, il n'est pas possible de copier-coller les clés que le joueur donne aux gardes pour passer les niveaux.
Comme ces clés sont des séquences de 32 chiffres hexadécimaux, il est très facile de faire des erreurs de frappe lorsqu'on les donne chiffre par chiffre.
Pour contourner cette difficulté, plusieurs approches sont possibles grâce à la console Javascript du navigateur : modifier l'état interne du jeu pour y injecter directement les clés, appeler les fonctions utilisées par les gardes pour valider et déchiffrer les données associées aux clés, ou encore simuler les frappes clavier.
Cette dernière possibilité se réalise simplement en lisant la documentation de Canvas Engine
\footnote{\url{http://canvasengine.net/}},
qui est le moteur utilisé par RPGJS.
En effet, ce moteur propose une fonction `Input.trigger` permettant d'injecter un événement comme une frappe clavier.

Toutefois il faut laisser un certain temps entre deux événements déclenchés, ce qui est résolu en ajoutant au jeu la fonction Javascript suivante:
```javascript
function enter_code(c) {
    if(!c) {
        RPGJS_Canvas.Input.trigger(RPGJS_Canvas.Enter, "press");
    } else {
        var k=c[0].toUpperCase().charCodeAt(0);
        RPGJS_Canvas.Input.trigger(k, "down");
        window.setTimeout('RPGJS_Canvas.Input.trigger('+k+', "up")', 10);
        window.setTimeout('enter_code("'+c.substr(1)+'")', 20);
    }
}
```

Il suffit alors lorsque le garde de chaque niveau demande une clé de copier dans la console Javascript une des lignes suivantes:
```javascript
// Level 1
enter_code('57d9f82b49c1eb3993cb82d26e37f69c'); // calc.zip
enter_code('368be8c1cc7cc70c2245030934301c15'); // SOS-Fant0me.zip
enter_code('1ac3d8c409e656380a06f6f2c6de6b4a'); // radio.zip, 2 points

// Level 2
enter_code('347d8c72720d6ec7a501583be0bccc0c'); // foo.zip
enter_code('e574b514667f6ab2d83047bb871a54f5'); // huge.zip
enter_code('e1fb7fd007493631c1156e5c87ebd51b'); // loader.zip

// Level 3
enter_code('23425038472508287335772085544035'); // strange.zip, 2 points
```
