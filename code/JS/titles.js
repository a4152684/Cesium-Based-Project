/*
 * @Description: 显示点云并漫游
 * @Author: longchen
 * @Date: 2020-08-01 10:20:00
 * @LastEditTime: 2020-08-01 16:07:24
 */
var viewer = new Cesium.Viewer("cesiumContainer");
// var viewer = new Cesium.Viewer("cesiumContainer", {
//     terrainProvider: Cesium.createWorldTerrain(),
// });
var scene = viewer.scene;

function setColorStyle(tileset) {
    tileset.style = new Cesium.Cesium3DTileStyle({
        color: {
            conditions: [
                ['${z} >= 10', 'color("purple", 0.5)'],
                ['${z} >= 5', 'color("red")'],
                ['true', 'color("blue")']
            ]
        }
    });
}

$(display).click(function () {
    var tileset = new Cesium.Cesium3DTileset({
        url: '../data/new_UTM50/tileset.json',
    });
    // alert(tileset.properties)
    scene.primitives.add(tileset);
    tileset.readyPromise.then(function (tileset) {
        var properties = tileset.properties;
        if (Cesium.defined(properties)) {
            for (var name in properties) {
                console.log(properties[name]);
            }
        }
        setColorStyle(tileset);
        viewer.zoomTo(tileset);
    });
});

$(del).click(function () {
    scene.primitives.removeAll();
    viewer.camera.flyHome();
});